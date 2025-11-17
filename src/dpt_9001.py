import struct
import math


class DPT9001Error(Exception):
    """Custom exception for DPT 9001 encoding/decoding errors."""
    pass


class DPT9001ValidationError(DPT9001Error):
    """Exception raised for validation errors in DPT 9001 operations."""
    pass


# DPT 9001 constants
DPT9001_MIN_VALUE = -671088.64
DPT9001_MAX_VALUE = 670760.96
DPT9001_PRECISION = 2  # Decimal places for rounding


def pack_dpt9001(value):
    """
    Packs a floating-point value into a 16-bit integer according to the DPT 9001 standard.

    Args:
        value (float): The floating-point value to be packed.

    Returns:
        int: The 16-bit integer representation of the floating-point value.

    Raises:
        DPT9001ValidationError: If the input value is out of range or invalid.
        TypeError: If the input is not a numeric type.
    """
    # Enhanced input validation
    if not isinstance(value, (float, int)):
        raise TypeError("Value must be a float or int.")
    
    # Handle NaN and infinity
    if isinstance(value, float):
        if math.isnan(value):
            raise DPT9001ValidationError("Cannot encode NaN values")
        if math.isinf(value):
            raise DPT9001ValidationError("Cannot encode infinity values")

    # Clamp the value within the supported range with better error message
    if value > DPT9001_MAX_VALUE or value < DPT9001_MIN_VALUE:
        raise DPT9001ValidationError(
            f"Value {value} is out of range for DPT 9001 encoding. "
            f"Valid range is [{DPT9001_MIN_VALUE}, {DPT9001_MAX_VALUE}]"
        )

    # Convert to integer mantissa with proper rounding
    signed_mantissa = int(round(value * 100))
    exp = 0  # Initialize the exponent

    # Normalize the mantissa to fit within 11 bits
    while signed_mantissa > 2047 or signed_mantissa < -2048:
        signed_mantissa //= 2
        exp += 1
        
        # Prevent infinite loop
        if exp > 15:
            raise DPT9001ValidationError("Value too large to encode in DPT 9001 format")

    # Prepare the 16-bit buffer
    buffer = bytearray(2)
    buffer[0] = (exp & 0x0F) << 3  # Encode the exponent

    if signed_mantissa < 0:
        signed_mantissa += 2048  # Handle the sign bit
        buffer[0] |= 0x80

    buffer[0] |= (signed_mantissa >> 8) & 0x07  # Add the high bits of the mantissa
    buffer[1] = signed_mantissa & 0xFF  # Add the low bits of the mantissa

    # Pack into a 16-bit integer
    return struct.unpack(">H", buffer)[0]


def unpack_dpt9001(value):
    """
    Unpacks a 16-bit integer into a floating-point value according to the DPT 9001 standard.

    Args:
        value (int): The 16-bit integer to be unpacked.

    Returns:
        float: The floating-point representation of the 16-bit integer.

    Raises:
        DPT9001ValidationError: If the input value is invalid.
        TypeError: If the input is not an integer.
    """
    if not isinstance(value, int):
        raise TypeError("Value must be an integer.")
    
    # Validate that the value is within 16-bit range
    if value < 0 or value > 0xFFFF:
        raise DPT9001ValidationError("Value must be a 16-bit unsigned integer (0-65535)")

    # Extract the high and low bytes
    h = (value >> 8) & 0xFF
    l = value & 0xFF

    # Extract the mantissa and handle the sign bit
    mantissa = ((h & 0x07) << 8) | l
    if h & 0x80:
        mantissa -= 2048

    # Extract the exponent
    exponent = (h >> 3) & 0x0F

    # Calculate the floating-point value with improved precision
    result = mantissa * 0.01 * (1 << exponent)
    
    # Round to specified precision for consistency
    return round(result, DPT9001_PRECISION)


def is_valid_dpt9001_value(value):
    """
    Check if a value is within the valid range for DPT 9001 encoding.
    
    Args:
        value: The value to check.
        
    Returns:
        bool: True if the value is valid for DPT 9001 encoding.
    """
    try:
        if not isinstance(value, (float, int)):
            return False
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return False
        return DPT9001_MIN_VALUE <= value <= DPT9001_MAX_VALUE
    except (TypeError, ValueError):
        return False


def get_dpt9001_range():
    """
    Get the valid range for DPT 9001 values.
    
    Returns:
        tuple: (min_value, max_value) tuple.
    """
    return (DPT9001_MIN_VALUE, DPT9001_MAX_VALUE)