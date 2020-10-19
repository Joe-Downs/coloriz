# All commands (and their necessary functions) for the coloriz bot

# Returns a tuple of RGB values from a given hex color value
def hexToRGB(hexValue):
    # If the hexValue string isn't 7 characters, it's not valid
    if len(hexValue) != 7:
        raise ValueError(f"{hexValue} is not the correct length")
    # If the hexValue string doesn't start with a '#', it's not valid
    if not hexValue.startswith('#'):
        raise ValueError(f"{hexValue} does not begin with #")
    red = hexValue[1]
    red += hexValue[2]
    red = int(red, 16)
    green = hexValue[3]
    green += hexValue[4]
    green = int(green, 16)
    blue = hexValue[5]
    blue += hexValue[6]
    blue = int(blue, 16)
    return (red, green, blue)


