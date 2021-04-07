import botCommands
import colorCommands
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

colorHelpMessage = "Choose your own color role with this command, replacing R G B with an RGB triplet. \n"
colorHelpMessage += "Replace the triplet with \"clear\" to clear your color role."

# Outputs a link to the table of color names, and some help
@bot.command()
async def colorhelp(ctx):
    message1 = "```To get a list of the named colors you can acquire, please visit:```"
    message2 = "<https://github.com/codebrainz/color-names/blob/master/output/colors.csv>"
    message3 = "```To get a named color from here, use the name of the leftmost side. "
    message3 += "If using a name with multiple words, either use underscores or "
    message3 += "put the name in quotation marks.```"
    message4 = "```If you would like a custom color, you can use this online"
    message4 += "tool to obtain a hex value:```"
    message5 = "<https://rgbcolorcode.com/>"
    await ctx.send(message1)
    await ctx.send(message2)
    await ctx.send(message3)
    await ctx.send(message4)
    await ctx.send(message5)

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
            color = await colorCommands.assignColor(ctx, args[0], args[1], args[2])
            message = f"Your color is {str(color)}."
            formatReminder = ""
    elif len(args) < 3:
        message = "Too few arguments!"
    if len(args) == 1:
        if args[0] == "clear":
            await colorCommands.removeColorRole(ctx)
            message = "Cleared your color role."
            formatReminder = ""
        elif args[0] == "random":
            red, green, blue = colorCommands.randomColor()
            color = await colorCommands.assignColor(ctx, red, green, blue)
            message = f"Your color is {str(color)}."
            formatReminder = ""
        # If it starts with a number sign, try to assign a color based off the
        # hex value
        elif args[0].startswith("#"):
            try:
                red, green, blue = botCommands.hexToRGB(args[0])
                color = await colorCommands.assignColor(ctx, red, green, blue)
                message = f"Your color is {str(color)}."
                formatReminder = ""
            except ValueError as error:
                message = str(error)
                formatReminder = ""
        else:
            try:
                color = await colorCommands.colorByName(ctx, args[0])
                message = f"Your color is {str(color)}"
            except NameError as error:
                message = str(error)
            formatReminder = ""
    message += formatReminder
    await ctx.send(message)

statsHelpMessage = "Show stats about this server's color roles"
@bot.command(help = statsHelpMessage,
             brief = "Get some stats!")
async def stats(ctx):
    roleCount = colorCommands.countColorRoles(ctx)
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
        await colorCommands.cleanupColors(ctx)

# Commands for testing various functionalities of the bot
@bot.command()
async def test(ctx, *args):
    if args[0] == "type":
        await ctx.send(f"The type of {args[1]} is {type(args[1])}")

bot.run(botToken)
