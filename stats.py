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

# Given a user, server ID, and the current timestamp updateStats() updates the
# entry in the table for the user's current color: editing the length from -1 to
# however many seconds they had the color for. (We could calculate the timestamp
# when needed by calling datetime.utcnow(), but for consistency's sake, we're
# using the same timestamp that will be used in the new database record.)
def updateStats(userID, serverID, curColor, curDatetime):
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
    prevDatetime = datetime.fromisoformat(prevTimestamp)
    length = (curDatetime - prevDatetime).total_seconds()
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
    timestamp = datetime.utcnow()
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
        if updateStats(userID, serverID, color, timestamp):
            return
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

# Given a userID, calcLongestColor() returns a string of the color the user had
# for the longest time, and the time they had it.
def calcLongestColor(userID, serverID):
    sqlCommand = f"""
SELECT max(length), color FROM colorHistory WHERE userID=? AND serverID=?
"""
    curs.execute(sqlCommand, (userID, serverID))
    result = curs.fetchone()
    maxLength = result[0]
    color = result[1]
    time = prettyLength(maxLength)
    longestColorString = f"{color} - {time}"
    return longestColorString

# Given a userID, calcShortestColor() returns a string of the color the user had
# for the longest time, and the time they had it.
def calcShortestColor(userID, serverID):
    sqlCommand = f"""
SELECT min(length), color FROM colorHistory WHERE userID=? AND serverID=? AND 
NOT length=-1
"""
    curs.execute(sqlCommand, (userID, serverID))
    result = curs.fetchone()
    minLength = result[0]
    color = result[1]
    time = prettyLength(minLength)
    shortestColorString = f"{color} - {time}"
    return shortestColorString

# ==============================================================================

# Given the ctx, this creates an embed, fills it with some info provided in ctx
# (author, color, etc.), and returns an Embed object.
def createEmbed(ctx):
    author = ctx.author
    authorNick = author.display_name
    authorUsername = author.name
    authorColor = author.color
    authorAvatar = str(author.avatar_url)
    userID = author.id
    serverID = ctx.guild.id
    longestColorString = calcLongestColor(userID, serverID)
    shortestColorString = calcShortestColor(userID, serverID)
    embed = discord.Embed(description = f"Stats for {authorNick}", color =
                          authorColor)
    embed.set_author(name = authorUsername, icon_url = authorAvatar)
    embed.add_field(name = "Longest Color", value = longestColorString,
                    inline = True)
    embed.add_field(name = "Shortest Color", value = shortestColorString,
                    inline = True)
    return embed
