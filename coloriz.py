import auth
import botCommands
import colorCommands
import commandConfig
import config
import discord
import sys
from discord.ext import commands
from pretty_help import PrettyHelp

owner_ID = 174362561385332736
botToken = config.getToken()
prefix = config.getPrefix()

intents = discord.Intents().default()
intents.members = True

bot = commands.Bot(command_prefix = prefix, intents = intents, help_command =
                   PrettyHelp())

# Outputs a link to the table of color names, and some help
@bot.command()
async def colorhelp(ctx):
    message1 = "```To get a list of the named colors you can acquire, please visit:```"
    message2 = "<https://unpkg.com/color-name-list/dist/colornames.html>"
    message3 = "```To get a named color from here, use the name of the leftmost side. "
    message3 += "If using a name with multiple words, either use underscores or "
    message3 += "put the name in quotation marks.```"
    message4 = "```If you would like a custom color, you can use this online "
    message4 += "tool to obtain a hex value:```"
    message5 = "<https://rgbcolorcode.com/>"
    await ctx.send(message1)
    await ctx.send(message2)
    await ctx.send(message3)
    await ctx.send(message4)
    await ctx.send(message5)

# =============================== Color Commands ===============================

class ColorCommands(commands.Cog, name = "Color Commands"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(name = "color", invoke_without_command = True,
                    aliases = commandConfig.getAliases("color"),
                    brief = commandConfig.getBrief("color"),
                    usage = commandConfig.getUsage("color"),
                    help = commandConfig.getHelp("color"))
    async def color(self, ctx, *args):
        # Calling the command with no arguments or subcommands has the bot
        # return a message.
        user = ctx.message.author
        colorMessage = colorCommands.getUserColor(ctx, user)
        # If there are arguments passed with the command, ask the user if they
        # wanted to set their color instead.
        if len(args) > 0:
            colorMessage += f"""
Colors are now assigned with ``{prefix}color set``, did you mean to do this?
"""
        await ctx.send(colorMessage)

    # color set is used for setting colors based off a given hex code, RGB
    # triplet, or a named color
    @color.command(name = "set",
                   aliases = commandConfig.getAliases("color set"),
                   brief = commandConfig.getBrief("color set"),
                   usage = commandConfig.getUsage("color set"),
                   help = commandConfig.getHelp("color set"))
    async def set(self, ctx, *args):
        setMessage = await botCommands.colorSet(ctx, args)
        await ctx.send(setMessage)

    # color random assigns the user with a completely random color.
    @color.command(name = "random",
                   aliases = commandConfig.getAliases("color random"),
                   brief = commandConfig.getBrief("color random"),
                   usage = commandConfig.getUsage("color random"),
                   help = commandConfig.getHelp("color random"))
    async def random(self, ctx):
        randomMessage = await botCommands.colorRandom(ctx)
        await ctx.send(randomMessage)

    @color.command(name = "clear",
                   aliases = commandConfig.getAliases("color clear"),
                   brief = commandConfig.getBrief("color clear"),
                   usage = commandConfig.getUsage("color clear"),
                   help = commandConfig.getHelp("color clear"))
    async def clear(self, ctx):
        clearMessage = await botCommands.colorClear(ctx)
        await ctx.send(clearMessage)

bot.add_cog(ColorCommands(bot))

# ==============================================================================

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

# Some 'sudo' commands can only be run by the bot owner; some by admins
@bot.command(help = sudoHelpMessage,
             brief = "Super secret!",
             usage = "[exit/stop | cleanup-colors]")
async def sudo(ctx, arg):
    sudoFailMessage = f"**{ctx.message.author.name}** {auth.failMessage}"
    if arg == "exit" or arg == "stop":
        # Checks if the message was sent by the bot owner
        # If not, tell the user and exit
        if (ctx.message.author.id != owner_ID):
            await ctx.send(sudoFailMessage)
            return
        else:
            await ctx.send("Sleep mode activated...")
            print("Stopping Bot...")
            await bot.close()
            sys.exit()
    if arg == "cleanup-colors":
        if auth.canManageRoles(ctx):
            await ctx.send("Clearing colors...")
            await colorCommands.cleanupColors(ctx)
        else:
            await ctx.send(sudoFailMessage)

# Commands for testing various functionalities of the bot
@bot.command()
async def test(ctx, *args):
    if args[0] == "type":
        await ctx.send(f"The type of {args[1]} is {type(args[1])}")
    if args[0] == "perm" or args[0] == "perms":
        if args[1] == "manage_roles":
            await ctx.send(f"{auth.canManageRoles(ctx)}")
bot.run(botToken)
