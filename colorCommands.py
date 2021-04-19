import csv
import random
import discord
import botCommands
import namedColors

# Returns the index position of the Bots top role in the guild's list of roles
def getBotTopRoleNum(ctx):
    botMember = ctx.guild.me
    botRoles = botMember.roles
    topBotRole = botRoles[len(botRoles) - 1]
    return ctx.guild.roles.index(topBotRole)
        

async def assignColor(ctx, red, green, blue):
    color = discord.Color.from_rgb(int(red), int(green), int(blue))
    user = ctx.message.author
    topRole = user.top_role
    for role in user.roles:
        if str(role).startswith("#"):
            await user.remove_roles(role)
            break
    needsNewRole = True
    for role in ctx.guild.roles:
        if role.name == str(color):
            print(f"{role.name} is {str(color)}")
            await user.add_roles(role)
            needsNewRole = False
            break
        
    if needsNewRole:
        role = await ctx.guild.create_role(name = str(color), color = color)
        await user.add_roles(role)
        # The top color role will be the one directly under the bot's own top role
        topColorRoleNum = getBotTopRoleNum(ctx) - 1
        try:
            await ctx.guild.edit_role_positions(positions = {role: topColorRoleNum})
        except:
            await ctx.send(f"Something went wrong moving {str(color)} to position {topColorRoleNum}")
    return color

async def cleanupColors(ctx):
    rolesDeleted = 0
    for role in ctx.guild.roles:
        if str(role).startswith("#"):
            if len(role.members) == 0:
                await role.delete(reason = "Unused")
                rolesDeleted += 1
    message = f"Deleted {rolesDeleted} roles."
    await ctx.send(message)

# Given a color name, this function will search the colors given in the
# colorNames.csv file for that name. If found, it will return the red, green,
# blue values pertaining to that color; if not, the user is notified. CSV from
# meodai's repo on GitHub.
# (https://github.com/meodai/color-names/blob/master/dist/colornames.csv)
def colorByName(name):
    # Replace any underscores in the name with spaces and make it lowercase
    name = name.replace("_", " ")
    name = name.lower()
    colorHex = namedColors.findNamedColorHex(name)
    red, green, blue = botCommands.hexToRGB(colorHex)
    return red, green, blue

def countColorRoles(ctx):
    roleCount = 0
    for role in ctx.guild.roles:
        if str(role).startswith("#"):
            roleCount += 1
    return roleCount

# Returns a message string containing the specified user's color. If the user
# does not have a color role, then return a message with such.
def getUserColor(ctx, user):
    for role in user.roles:
        if str(role).startswith("#"):
            return f"**{user.nick}'s** color is {str(role)}"
    return f"**{user.nick}** does not have a color role"

# Chooses three random numbers, each 0-255 and returns them
def randomColor():
    random.seed()
    red = random.randint(0,255)
    green = random.randint(0,255)
    blue = random.randint(0,255)
    return red, green, blue

async def removeColorRole(ctx):
    user = ctx.message.author
    for role in user.roles:
        if str(role).startswith("#"):
            await user.remove_roles(role)
            break
