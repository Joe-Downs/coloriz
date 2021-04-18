# Python Modules
import re
# Third-Party Modules
# Custom Modules
import colorCommands
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

# =============================== Color Commands ===============================

# parseRGB() parses a user's input into three integers. It checks to makes sure
# the triplet is well-formed and within bounds [0,255]. If everything checks out,
# the red, green, and blue values are returned (in order); if not, errors with
# appropriate messages for the user are raised.
def parseRGB(rgbInput):
    # We want to mach three numbers, each with 1-3 digits.  They might be
    # separated by spaces, commas, or a mix of both. The digitPattern is used to
    # match one number at a time, utilizing re.findall(), which returns a list
    # of all the found values.  The pattern means: "find 1-3 instances of a
    # digit."
    numPattern = r"[\d]{1,3}"
    result = re.findall(numPattern, rgbInput)
    # If the regex finds nothing, that means there wasn't a single digit in the
    # input, assume the user wanted a named color.
    if len(result) == 0:
        raise NameError("No integers were found in {rgbInput}")
    # Check that ONLY three numbers were found.
    if len(result)  != 3:
        raise ValueError("An RGB triplet should only have three integers")
    # Check the results to make sure they're valid RGB values [0,255].
    for value in result:
        if not 0 <= int(value) <= 255:
            raise ValueError("RGB values must be between 0 and 255")
    red, green, blue = int(result[0]), int(result[1]), int(result[2])
    return red, green, blue

# colorSet() sets a user's color based of a given hex code, RGB triplet, or a
# named color. Parsing is all done here, not in coloriz.py. Returns a string of
# the color assigned or raises an error with relevant info on what went wrong;
# this error can be printed out by the bot as a message to the user.
async def colorSet(ctx, args):
    # If there's only one argument, it *should* either be a hex code or a named
    # color.
    if len(args) == 1:
        # If it begins with a '#' it should be a hex code; if it doesn't, it
        # might be a named color.
        if args[0].startswith("#"):
            try:
                red, green, blue = hexToRGB(args[0])
            except ValueError as hexError:
                return hexError
        # See if it's a named color, if not, try to parse it into RGB
        try:
            color = await colorCommands.colorByName(ctx, args[0])
        except NameError as colorNameError:
            try:
                red, green, blue = parseRGB(args[0])
                color = await colorCommands.assignColor(ctx, red, green, blue)
            except NameError:
                # If a NameError is caught from parseRGB(), there were no digits
                # found in the input, thus we're assuming the user wanted a
                # named color. Return the error message from colorByName()
                # saying such.
                return colorNameError
            except ValueError as parseError:
                return parseError
    else:
        # Combine the rest of the arguments and parse them with parseRGB().
        arguments = ""
        try:
            for arg in args:
                arguments += arg
            red, green, blue = parseRGB(arguments)
        except ValueError as parseError:
            return parseError
        color = await colorCommands.assignColor(ctx, red, green, blue)
    return f"Your color is **{str(color)}**"

# colorRandom() sets a user's color to a completely random color. It takes no
# arguments other than the ctx and returns a string that states what the user's
# new color is.
async def colorRandom(ctx):
    # Get three random integers between [0.255] and assign the user's color with
    # them.
    red, green, blue = colorCommands.randomColor()
    color = await colorCommands.assignColor(ctx, red, green, blue)
    return f"Your color is **{str(color)}**"

# colorClear() clears the user's color. It takes no arguments other than ctx and
# returns a string saying the user's color was cleared.
async def colorClear(ctx):
    await colorCommands.removeColorRole(ctx)
    return "Your color role has been cleared"

# ==============================================================================
