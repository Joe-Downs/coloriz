import csv
import math
import unicodedata
import requests

# (Re)download the colorNames.csv from meodai's repo on GitHub
# https://github.com/meodai/color-names
colorNamesURL = "https://raw.githubusercontent.com/meodai/color-names/master/dist/colornames.csv"
r = requests.get(colorNamesURL)

# Write the data to a csv, overwriting any previous versions
with open("colorNames.csv", "wb") as f:
    f.write(r.content)
f.close()

# Load names and RGB values from colorNames.csv into a list of dictionaries to
# be used by the colorByName() function. The columns, in order, are name, hex
colorDictList = []
with open("colorNames.csv", newline='') as csvColors:
    colorReader = csv.DictReader(csvColors)
    for row in colorReader:
        colorDictList.append(row)
csvColors.close()

# Normalize every name in the list of color dictionaries (replace all 'special'
# characters with their ASCII counterparts, e.g., á becomes a). While this may
# not be the ideal solution, it will work fine enough for these purposes.
for color in colorDictList:
    # If the color name is already normalized, skip it
    if unicodedata.is_normalized("NFD", color["name"]):
        continue
    # Normalize the color name and remove the decomposed non-ASCII strings
    norm = unicodedata.normalize("NFD", color["name"])
    encodedString =  norm.encode("ascii", "ignore")
    color["name"] = encodedString.decode()

# Searches through the list of colorDicts and returns the hex value for the
# given color if the name is found. If not, a NameError is raised
def findNamedColorHex(color):
    # These bounds are changed as the binary search occurs
    lowerBound = 0
    upperBound = len(colorDictList) - 1
    # Search until the bounds overlap
    while lowerBound <= upperBound:
    #for foo in range(0,20):
        # Add the lower bound to the section length, divide by 2, and floor it,
        # getting a whole number instead of a decimal, in case of odd-numbered
        # lengths. Adding the lower bound is necessary because the length
        # between two bounds is NOT the median of those two bounds
        middleIndex = math.floor((lowerBound + upperBound) / 2)
        # If less than, the color comes before the middle index (earlier in the
        # alphabet) disregard the lower half and repeat. If greater, the color
        # comes after the middle index (later in the alphabet) of that section,
        # disregard the upper half and repeat. If the color is equal to the one
        # at the middle index, then we've found our color
        if color < colorDictList[middleIndex]["name"].lower():
            # Lower bound is unchanged
            upperBound = middleIndex - 1
        elif color > colorDictList[middleIndex]["name"].lower():
            lowerBound = middleIndex + 1
            # Upper bound is unchanged
        elif color == colorDictList[middleIndex]["name"].lower():
            return colorDictList[middleIndex]["hex"]
    # If the while loop exits without returning anything, the color was not
    # found, raise an error
    raise NameError(f"\"{color}\" is not a named color")

# Search through the list of named colors and return a list of color names that
# match the given search term.
def searchNamedColors(name):
    matches = []
    for namedColor in colorDictList:
        if name in namedColor["name"].lower():
            matches.append(namedColor["name"])
    return matches
