import struct


class DPT9001Error(Exception):
    """Custom exception for DPT 9001 encoding/decoding errors."""
    pass


def pack_dpt9001(value):
    """
    Packs a floating-point value into a 16-bit integer according to the DPT 9001 standard.

    Args:
        value (float): The floating-point value to be packed.

    Returns:
        int: The 16-bit integer representation of the floating-point value.

    Raises:
        DPT9001Error: If the input value is out of range.
    """
    if not isinstance(value, (float, int)):
        raise TypeError("Value must be a float or int.")

    # Clamp the value within the supported range
    if value > 670760.96 or value < -671088.64:
        raise DPT9001Error(f"Value {value} is out of range for DPT 9001 encoding.")

    signed_mantissa = int(value * 100)  # Convert the float to an integer mantissa
    exp = 0  # Initialize the exponent

    # Normalize the mantissa to fit within 11 bits
    while signed_mantissa > 2047 or signed_mantissa < -2048:
        signed_mantissa //= 2
        exp += 1

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
    """
    if not isinstance(value, int):
        raise TypeError("Value must be an integer.")

    # Extract the high and low bytes
    h = (value >> 8) & 0xFF
    l = value & 0xFF

    # Extract the mantissa and handle the sign bit
    mantissa = ((h & 0x07) << 8) | l
    if h & 0x80:
        mantissa -= 2048

    # Extract the exponent
    exponent = (h >> 3) & 0x0F

    # Calculate the floating-point value
    return round(mantissa * 0.01 * (1 << exponent), 2)