# This module handles everything to do with recording and presenting stats. This
# includes saving stats to the database, computing a user / server's stats, and
# creating the embeds to present to the user.

import config
from datetime import datetime
import discord
import sqlite3

conn = sqlite3.connect("coloriz.db")

# Given the ctx, this records all the stats necessary into the table. The
# function uses the ctx to grab data about the user and server. The function
# gets the user's color from the ctx.
def recordStats(ctx):
    userID = ctx.message.author.id
    serverID = ctx.guild.id
    timestamp = str(datetime.utcnow())
    color = str(ctx.message.author.color)
    # colorHistory columns go: sqlID, userID, serverID, color, timestamp
    sqlCommand = f"""
INSERT INTO colorHistory VALUES (NULL, ?, ?, ?, "{timestamp}")
"""
    conn.execute(sqlCommand, (userID, serverID, color,))
    conn.commit()

# Given the ctx, this creates an embed, fills it with some info provided in ctx
# (author, color, etc.), and returns an Embed object.
def createEmbed(ctx):
    authorNick = ctx.author.display_name
    authorColor = ctx.author.color
    embed = discord.Embed(title=f"Stats for {authorNick}", color = authorColor)
    return embed
