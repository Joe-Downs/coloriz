import configTest
import discord
import sys

from discord.ext import commands

owner_ID = 174362561385332736
botToken = configTest.getToken()
prefix = configTest.getPrefix()

bot = commands.Bot(command_prefix = prefix)
    
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
        print(f"Creating role {str(color)}")
        role = await ctx.guild.create_role(name = str(color),
                                           color = color)
        await user.add_roles(role)
        topColorRoleNum = len(ctx.guild.roles) - 3
        await ctx.guild.edit_role_positions(positions = {role: topColorRoleNum})
    return color

@bot.command()
async def color(ctx, red, green, blue):
    color = await assignColor(ctx, red, green, blue)
    messageString = f"Your color is {str(color)}"
    await ctx.send(messageString)


# 'sudo' commands can only be run by the bot owner
@bot.command()
async def sudo(ctx, arg):
    # Checks if the message was sent by the bot owner
    # If not, tell the user and exit
    if (ctx.message.author.id != owner_ID):
        await ctx.send(ctx.message.author.name +
                       " is not in the sudoers file." +
                       " This incident will be reported.")
        return

    if (arg == "exit" or arg == "stop"):
        await ctx.send("Sleep mode activated...")
        print("Stopping Bot...")
        sys.exit()

bot.run(botToken)
