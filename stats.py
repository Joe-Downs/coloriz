# This module handles everything to do with recording and presenting stats. This
# includes saving stats to the database, computing a user / server's stats, and
# creating the embeds to present to the user.

import config
from datetime import datetime
import discord
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

# Given the ctx, this creates an embed, fills it with some info provided in ctx
# (author, color, etc.), and returns an Embed object.
def createEmbed(ctx):
    authorNick = ctx.author.display_name
    authorColor = ctx.author.color
    embed = discord.Embed(title=f"Stats for {authorNick}", color = authorColor)
    return embed
