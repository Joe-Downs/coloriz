import discord

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
        role = await ctx.guild.create_role(name = str(color), color = color)
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
