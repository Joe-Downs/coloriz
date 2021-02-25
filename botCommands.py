# All commands (and their necessary functions) for the coloriz bot

# Returns a three values (red, green, blue) from a given hex color value
def hexToRGB(hexValue):
    # If the hexValue string isn't 7 characters, it's not valid
    if len(hexValue) != 7:
        raise ValueError(f"{hexValue} is not the correct length")
    # If the hexValue string doesn't start with a '#', it's not valid
    if not hexValue.startswith('#'):
        raise ValueError(f"{hexValue} does not begin with #")
    red = int(hexValue[1] + hexValue[2], 16)
    green = int(hexValue[3] + hexValue[4], 16)
    blue = int(hexValue[5] + hexValue[6], 16)
    return red, green, blue
