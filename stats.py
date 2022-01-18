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
def updateStats(userID, serverID, curDatetime):
    # If an entry has a length of -1, then that is the user's currently active
    # color, so we'll need update with how long they had that one.
    sqlCommand = f"""
SELECT timestamp FROM colorHistory WHERE length=-1 AND userID=? AND serverID=?
"""
    curs.execute(sqlCommand, (userID, serverID))
    prevTimestamp = curs.fetchone()
    # If it's None, then the user does not have an active color on this server:
    # we don't have to calculate how long they had their color. Just insert a
    # new record into the database. (Which is done in recordStats().)
    if prevTimestamp == None:
        pass
    else:
        prevTimestamp = prevTimestamp[0]
        prevDatetime = datetime.fromisoformat(prevTimestamp)
        length = (curDatetime - prevDatetime).total_seconds()
        updateCommand = f"""
UPDATE colorHistory SET length=? WHERE length=-1 AND userID=? AND serverID=?
"""
        curs.execute(updateCommand, (length, userID, serverID))
    return

# Given the ctx, this records all the stats necessary into the table. The
# function uses the ctx to grab data about the user and server. The function
# gets the user's color from the ctx.
def recordStats(ctx):
    userID = ctx.message.author.id
    serverID = ctx.guild.id
    timestamp = datetime.utcnow()
    color = str(ctx.message.author.color)
    updateStats(userID, serverID, timestamp)
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
