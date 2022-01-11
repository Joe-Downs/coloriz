# This module handles everything to do with recording and presenting stats. This
# includes saving stats to the database, computing a user / server's stats, and
# creating the embeds to present to the user.

import discord

# Given the ctx, this creates an embed, fills it with some info provided in ctx
# (author, color, etc.), and returns an Embed object.
def createEmbed(ctx):
    authorNick = ctx.author.display_name
    authorColor = ctx.author.color
    embed = discord.Embed(title=f"Stats for {authorNick}", color = authorColor)
    return embed
