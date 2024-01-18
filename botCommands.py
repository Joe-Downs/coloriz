# Python Modules
import re
import time
# Third-Party Modules
# Custom Modules
import colorCommands
import namedColors
import stats
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

# parseHex() parses a user's hex input into three integers. It checks to make
# sure it is a valid hex code and converts it to an RGB triplet (via hexToRGB())
# in the form of three values returned: red, green, blue. If it's not a valid
# hex code, raise an error with some relevant information.
def parseHex(hexInput):
    # Pattern to find exactly six digits or lower- and uppercase characters A-F
    hexPattern = "#[0-9,a-f,A-F]{6,6}"
    hexSearch = re.search(hexPattern, hexInput)
    if hexSearch == None:
        raise ValueError(f"{hexInput} is not a valid hex code")
    else:
        return hexToRGB(hexSearch.group())

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
    # Combine the arguments into one string so it can easily be parsed with
    # regex. Remove trailing / leading whitespace after combining.
    arguments = ""
    for arg in args:
        arguments += f"{arg} "
    arguments = arguments.strip()
    # This pattern is used to check if there are at least two sets of numbers
    # separated by non-numeric characters. If there are, then we can be pretty
    # confident that it is not a named color and parseRGB() can be called. Thus,
    # we can return any errors thrown by parseRGB().
    rgbPattern = r"[\D]*[0-9]{1,}[\D]{1,}[0-9]{1,}[\D]*[0-9]{1,}[\D]*"
    # If it starts with a '#', try to parse it as a hex code. If not, check if
    # it could be a valid RGB triplet with the above regex pattern. If it's not,
    # then see if it's a named color.
    if arguments.startswith("#"):
        try:
            red, green, blue = parseHex(arguments)
        except ValueError as hexError:
            return hexError
    elif re.search(rgbPattern, arguments):
        try:
            red, green, blue = parseRGB(arguments)
        except ValueError as rgbError:
            return rgbError
    else:
        try:
            red, green, blue = colorCommands.colorByName(arguments)
        except NameError as colorNameError:
            return colorNameError
    color = await colorCommands.assignColor(ctx, red, green, blue)
    stats.recordStats(ctx, str(color))
    return f"Your color is **{str(color)}**"

async def colorSearch(ctx, args):
    arguments = ""
    for arg in args:
        arguments += f"{arg} "
    arguments = arguments.strip()
    startTime = time.time()
    matches = namedColors.searchNamedColors(arguments)
    endTime = time.time()
    timeTaken = "{:.4}".format(endTime - startTime)
    returnString = f"Found {len(matches)} Colors in {timeTaken}s:\n```"
    for match in matches[0:50]:
        returnString += f"- {match}\n"
    returnString += "Only showing 50 colors...```"
    return returnString

# colorRandom() sets a user's color to a completely random color. It takes no
# arguments other than the ctx and returns a string that states what the user's
# new color is.
async def colorRandom(ctx):
    # Get three random integers between [0.255] and assign the user's color with
    # them.
    red, green, blue = colorCommands.randomColor()
    color = await colorCommands.assignColor(ctx, red, green, blue)
    stats.recordStats(ctx, str(color))
    return f"Your color is **{str(color)}**"

# colorClear() clears the user's color. It takes no arguments other than ctx and
# returns a string saying the user's color was cleared.
async def colorClear(ctx):
    await colorCommands.removeColorRole(ctx)
    stats.recordStats(ctx, None)
    return "Your color role has been cleared"

# ==============================================================================
