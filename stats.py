# This module handles everything to do with recording and presenting stats. This
# includes saving stats to the database, computing a user / server's stats, and
# creating the embeds to present to the user.

import config
from datetime import datetime
import discord
import math
import sqlite3

conn = sqlite3.connect("coloriz.db")
curs = conn.cursor()

# Given a previous timestamp, this calculates how long ago (in seconds) the
# previous timestamp was. Returns said length.
def calcLengthSec(prevTimestamp):
    curDatetime = datetime.utcnow()
    prevDatetime = datetime.fromisoformat(prevTimestamp)
    length = (curDatetime - prevDatetime).total_seconds()
    return length

# Given a user, server ID, and the user's current color, updateStats() updates
# the entry in the table for the user's current color: editing the length from
# -1 to however many seconds they had the color for.
def updateStats(userID, serverID, curColor):
    # If an entry has a length of -1, then that is the user's currently active
    # color, so we'll need update with how long they had that one.
    sqlCommand = f"""
SELECT color, timestamp FROM colorHistory WHERE length=-1 AND userID=? AND serverID=?
"""
    curs.execute(sqlCommand, (userID, serverID))
    result = curs.fetchone()
    print(result)
    # If the result is None, then the user does not have an active color on this
    # server: we don't have to calculate how long they had their color. Just
    # insert a new record into the database. (Which is done in recordStats().)
    if result == None:
        return
    prevColor = result[0]
    prevTimestamp = result[1]
    # If the previous color is equal to the current color, then the user hasn't
    # *really* changed their color. We neither need to update the length, nor
    # add a new record.
    if prevColor == curColor:
        return True
    length = calcLengthSec(prevTimestamp)
    updateCommand = f"""
UPDATE colorHistory SET length=? WHERE length=-1 AND userID=? AND serverID=?
"""
    curs.execute(updateCommand, (length, userID, serverID))
    conn.commit()
    return

# Given the ctx, and the hex value of the user's NEW color, this records all the
# stats necessary into the table. The function uses the ctx to grab data about
# the user and server.
def recordStats(ctx, color):
    userID = ctx.message.author.id
    serverID = ctx.guild.id
    # We want all the colors to be uppercase (I like how that looks) so we can
    # safely compare two colors later. It goes in a try block so that we can
    # catch the AttributeError if color is None (like when the user clears their
    # color)
    try:
        color = color.upper()
    except AttributeError:
        # If the color is None, that means the user cleared their color: update
        # their previous color length (done above), but don't add a new
        # record. (We should be able to trust that if an AttributeError is
        # raised, the color is None, but just to be safe, we'll check here.
        if color == None:
            return
    # Regardless if there's an error or not, we still want to update the stats.
    finally:
        # If it returns true, we don't need to add a new record into the table.
        if updateStats(userID, serverID, color):
            return
    timestamp = datetime.utcnow()
    # colorHistory columns go: sqlID, userID, serverID, color, timestamp, length
    sqlCommand = f"""
INSERT INTO colorHistory VALUES (NULL, ?, ?, ?, ?, ?)
"""
    curs.execute(sqlCommand, (userID, serverID, color, str(timestamp), -1))
    conn.commit()

# ============================ Calculating Functions ===========================
# Functions for analyzing the database and returning datapoints to be used in
# the embed sent back to the user.

# Takes a length in seconds, and converts that to a nicer, more general format
# ("5 minutes", "10 days", "1 year", etc.)
def prettyLength(length):
    # Convert the length (a float originally with microseconds), because we
    # don't need to send that much precision in the embed.
    length = int(length)
    if length < 60:
        prettyLengthString = f"{length} second"
    elif length < 3600:
        prettyLengthString = f"{math.floor(length/60)} minute"
    elif length < 86400:
        prettyLengthString = f"{math.floor(length/3600)} hour"
    elif length < 604800:
        prettyLengthString = f"{math.floor(length/86400)} day"
    elif length < 2628000:
        prettyLengthString = f"{math.floor(length/604800)} week"
    elif length < 31540000:
        prettyLengthString = f"{math.floor(length/2628000)} month"
    else:
        prettyLengthString = f"{math.floor(length/31540000)} year"
    # If the value is not 1, make the unit plural
    if not prettyLengthString.startswith("1 "):
        prettyLengthString = prettyLengthString + "s"
    return prettyLengthString

# Given a userID and serverID, calcColorExtremes() calculates the shortest and
# longest color the user had on that server. It returns two strings for the
# longest and shortest colors, respectively.
def calcColorExtremes(userID, serverID):
    returnStrings = []
    for extreme in ["max", "min"]:
        sqlCommand = f"""
SELECT {extreme}(length), color FROM colorHistory WHERE userID=? AND serverID=?
AND NOT length=-1
"""
        curs.execute(sqlCommand, (userID, serverID))
        result = curs.fetchone()
        length = result[0]
        color = result[1]
        returnStrings.append((color, length))
    return returnStrings[0], returnStrings[1]

# Given a userID and serverID, calculate the length of the user's current color,
# and return the length and color, respectively. This will be compared to the
# longest/shortest length from the database, so the true longest/shortest can be
# chosen, allowing for a "live" length.
def calcCurrentLength(userID, serverID):
    sqlCommand = f"""
SELECT color, timestamp FROM colorHistory WHERE userID=? AND serverID=? AND
LENGTH=-1
"""
    curs.execute(sqlCommand, (userID, serverID))
    result = curs.fetchone()
    color = result[0]
    start = result[1]
    length = calcLengthSec(start)
    return (color, length)

# Given the current length of the user's color, the longest/shortest database
# length, check which ones are the true extremes. e.g., if the current length is
# shorter than the database length, the current length is the true
# shortest. Returns the strings for the longest and shortest colors
def checkExtremes(currentColor, longestColor, shortestColor):
    current = currentColor[1]
    currentName = currentColor[0]
    longest = longestColor[1]
    longestName = longestColor[0]
    shortest = shortestColor[1]
    shortestName = shortestColor[0]
    shortestColorString = f"{shortestName} - {prettyLength(shortest)} "
    longestColorString = f"{longestName} - {prettyLength(longest)}"
    if current > longest:
        longestColorString = f"{currentName} - {prettyLength(current)}\nThat's your current color! :o"
    elif current < shortest:
        shortestColorString = f"{currentName} - {prettyLength(current)}\nThat's your current color! :o"
    return longestColorString, shortestColorString
# ==============================================================================

# Given a serverID and user object, this creates an embed, fills it with some
# info provided from the object (name, color, etc.), and returns an Embed
# object.
def createEmbed(serverID, user):
    userID = user.id
    userNick = user.display_name
    username = user.name
    userColor = user.color
    userAvatar = str(user.avatar_url)
    embed = discord.Embed(description = f"Stats for {userNick}", color =
                          userColor)
    embed.set_author(name = username, icon_url = userAvatar)
    # If the user doesn't have a color, then the SQL commands in the calc...()
    # functions will return a NoneType, which will raise a TypeError. For now,
    # we'll just do this, and add a little nicer solution later.
    try:
        longestColor, shortestColor = calcColorExtremes(userID, serverID)
        curColor = calcCurrentLength(userID, serverID)
        longestColorString, shortestColorString = checkExtremes(curColor,
                                                                longestColor,
                                                                shortestColor)
        currentColorString = f"{curColor[0]} - {prettyLength(curColor[1])}"
        embed.add_field(name = "Current Color", value = currentColorString,
                        inline = False)
        embed.add_field(name = "Longest Color", value = longestColorString,
                        inline = True)
        embed.add_field(name = "Shortest Color", value = shortestColorString,
                        inline = True)
    except TypeError:
        embed.add_field(name = "You haven't had any colors on this server", value = "D:!!!")
    return embed
