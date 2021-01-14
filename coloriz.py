import botCommands
import config
import discord
import sys

from discord.ext import commands

owner_ID = 174362561385332736
botToken = config.getToken()
prefix = config.getPrefix()

intents = discord.Intents().default()
intents.members = True

bot = commands.Bot(command_prefix = prefix, intents = intents)

# Returns the index position of the Bots top role in the guild's list of roles
def getBotTopRoleNum(ctx):
    botMember = ctx.guild.me
    botRoles = botMember.roles
    return len(botRoles) - 1
    
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
        role = await ctx.guild.create_role(name = str(color),
                                           color = color)
        await user.add_roles(role)
        # The top color role will be the one directly under the bot's own top role
        topColorRoleNum = getBotTopRoleNum(ctx) - 1
        await ctx.guild.edit_role_positions(positions = {role: topColorRoleNum})
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

def countColorRoles(ctx):
    roleCount = 0
    for role in ctx.guild.roles:
        if str(role).startswith("#"):
            roleCount += 1
    return roleCount

async def removeColorRole(ctx):
    user = ctx.message.author
    for role in user.roles:
        if str(role).startswith("#"):
            await user.remove_roles(role)
            break

colorHelpMessage = "Choose your own color role with this command, replacing R G B with an RGB triplet. \n"
colorHelpMessage += "Replace the triplet with \"clear\" to clear your color role."
        
@bot.command(help = colorHelpMessage,
             brief = "Change your color!",
             usage = "[R G B | clear]")
async def color(ctx, *args):
    message = ""
    formatReminder = " Please make sure to follow the pattern"
    formatReminder += f" ``{prefix}color [R] [G] [B]`` and try again."
    if len(args) > 3:
        message = "Too many arguments!"
    elif len(args) == 3:
        isValid = True
        for arg in args:
            try:
                int(arg)
            except:
                message = "Arguments are not integers!"
                isValid = False
                break
            if not 0 <= int(arg) <= 255:
                message = "Arguments are not between 0-255!"
                isValid = False
                break
        if isValid:
            color = await assignColor(ctx, args[0], args[1], args[2])
            message = f"Your color is {str(color)}."
            formatReminder = ""
    elif len(args) < 3:
        message = "Too few arguments!"
    if len(args) == 1:
        if args[0] == "clear":
            await removeColorRole(ctx)
            message = "Cleared your color role."
            formatReminder = ""
        else:
            try:
                rgbTuple = botCommands.hexToRGB(args[0])
                red = rgbTuple[0]
                green = rgbTuple[1]
                blue = rgbTuple[2]
                color = await assignColor(ctx, red, green, blue)
                message = f"Your color is {str(color)}."
                formatReminder = ""
            except ValueError as error:
                message = str(error)
                formatReminder = ""
    message += formatReminder
    await ctx.send(message)

statsHelpMessage = "Show stats about this server's color roles"
@bot.command(help = statsHelpMessage,
             brief = "Get some stats!")
async def stats(ctx):
    roleCount = countColorRoles(ctx)
    message = f"**{str(ctx.guild)}** has {roleCount} color roles!"
    await ctx.send(message)

sudoHelpMessage = "These commands can only be run by server admins or the bot owner\n"
sudoHelpMessage += "exit/stop ----------- stops the bot\n"
sudoHelpMessage += "cleanup-colors ------ removes color roles not assigned to any members"

# 'sudo' commands can only be run by the bot owner
@bot.command(help = sudoHelpMessage,
             brief = "Super secret!",
             usage = "[exit/stop | cleanup-colors]")
async def sudo(ctx, arg):
    # Checks if the message was sent by the bot owner
    # If not, tell the user and exit
    if (ctx.message.author.id != owner_ID):
        await ctx.send(ctx.message.author.name +
                       " is not in the sudoers file." +
                       " This incident will be reported.")
        return

    if arg == "exit" or arg == "stop":
        await ctx.send("Sleep mode activated...")
        print("Stopping Bot...")
        await bot.close()
        sys.exit()
        
    if arg == "cleanup-colors":
        await ctx.send("Clearing colors...")
        await cleanupColors(ctx)

bot.run(botToken)
