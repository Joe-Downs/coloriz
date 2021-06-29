# This file provides "getter" functions to retrieve the help messages from the
# JSON file which stores the various texts needed by discord.py's builtin help
# command.

import copy
import json

# Custom exception to be raised when a command is not found in the JSON.
class NameNotFoundError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name} was not found"

# Load the JSON file into Python data structures (lists and dictionaries).
with open("commandConfig.json") as commandHelp:
    commandConfig = json.load(commandHelp)

# ======================== Helper Functions for Getters ========================

# Given a list of command JSON objects, return a Python dict of the one which
# name matches the given searchName. If none is found, raise a
# NameNotFoundError.
def findNameInList(searchName, searchList):
    for command in searchList:
        if command["name"] == searchName:        
            return command
    raise NameNotFoundError(searchName)

# Returns the dictionary representing the JSON object of a given
# (sub)command. For instance, if "color clear" is given, the JSON object for
# just "color" is discarded. Thus, theDict["name"] would return "clear". If the
# given command is not in the JSON file, pass along the NameNotFoundError raised
# by findNameInList().
def trimCommandConfig(command):
    splitCommands = command.split(" ")
    trimmedJSON = copy.deepcopy(commandConfig)
    lastCommand = splitCommands[len(splitCommands) - 1]
    for command in splitCommands:
        # If it's a list of commands, then search through it for the command. If
        # its name is the last command in the splitCommands list, then it's the
        # deepest subcommand; return it. Otherwise, we haven't reached the
        # deepest yet, so we need the next subcommand level.
        if type(trimmedJSON) == list:
            trimmedJSON = findNameInList(command, trimmedJSON)
        if trimmedJSON["name"] == lastCommand:
            return trimmedJSON
        else:
            trimmedJSON = trimmedJSON["subcommands"]
    return trimmedJSON

# ============================== Getter Functions ==============================
# Each of these functions returns a list or string of the given (sub)command's
# respective field. If the given command is not found, pass along the
# NameNotFoundError raised by findNameInList() and passed by
# trimCommandConfig().

# getAliases() returns a list of strings
def getAliases(command):
    trimmedJSON = trimCommandConfig(command)
    return trimmedJSON["aliases"]

# getBrief() returns a string
def getBrief(command):
    trimmedJSON = trimCommandConfig(command)
    return trimmedJSON["brief"]

# getUsage() returns a string
def getUsage(command):
    trimmedJSON = trimCommandConfig(command)
    return trimmedJSON["usage"]

# getHelp() returns a string
def getHelp(command):
    trimmedJSON = trimCommandConfig(command)
    helpList = trimmedJSON["help"]
    # Concatenates the list of strings into one string to be returned. The help
    # is stored as a list of strings due to JSON's inability to have multi-line
    # strings.
    helpString = ""
    for fragment in helpList:
        helpString += fragment
    return helpString

# ==============================================================================

