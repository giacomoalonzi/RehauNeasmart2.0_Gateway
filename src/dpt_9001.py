import struct

def pack_dpt9001(f):
    """
    Packs a floating-point value into a 16-bit integer according to the DPT 9001 standard.

    The DPT 9001 format is used in building automation systems to represent floating-point values
    in a compact 16-bit format. This function converts a floating-point value into this format.

    Args:
        f (float): The floating-point value to be packed.

    Returns:
        int: The 16-bit integer representation of the floating-point value.
    """
    buffer = bytearray([0, 0])  # Initialize a 2-byte buffer

    # Clamp the input value to the range supported by DPT 9001
    if f > 670760.96:
        f = 670760.96
    elif f < -671088.64:
        f = -671088.64

    signed_mantissa = int(f * 100)  # Convert the float to an integer mantissa
    exp = 0  # Initialize the exponent

    # Normalize the mantissa to fit within 11 bits
    while signed_mantissa > 2047 or signed_mantissa < -2048:
        signed_mantissa //= 2
        exp += 1

    # Pack the exponent into the buffer (4 bits)
    buffer[0] |= (exp & 15) << 3

    # Handle the sign bit and adjust the mantissa if negative
    if signed_mantissa < 0:
        signed_mantissa += 2048
        buffer[0] |= 1 << 7

    mantissa = signed_mantissa

    # Pack the mantissa into the buffer (11 bits)
    buffer[0] |= ((mantissa >> 8) & 7) & 0xFF
    buffer[1] |= mantissa & 0xFF

    # Convert the buffer to a 16-bit integer
    return struct.unpack('>H', buffer)[0]

def unpack_dpt9001(i):
    """
    Unpacks a 16-bit integer into a floating-point value according to the DPT 9001 standard.

    The DPT 9001 format is used in building automation systems to represent floating-point values
    in a compact 16-bit format. This function converts a 16-bit integer in this format back into
    a floating-point value.

    Args:
        i (int): The 16-bit integer to be unpacked.

    Returns:
        float: The floating-point representation of the 16-bit integer.
    """
    h = (i >> 8) & 0xFF  # Extract the high byte
    l = i & 0xFF  # Extract the low byte

    m = (int(h) & 7) << 8 | int(l)  # Combine the mantissa bits
    if (h & 0x80) == 0x80:  # Check the sign bit
        m -= 2048  # Adjust the mantissa if negative

    e = (h >> 3) & 15  # Extract the exponent

    f = 0.01 * float(m) * float(1 << e)  # Calculate the floating-point value

    return round(f, 2)  # Return the value rounded to 2 decimal places