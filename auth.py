import discord

# Functions for authenticating whether a user has the required permissions to
# perform an action

# Message for if a user does not have the right permissions
failMessage = "is not in the sudoers file. This incident will be reported."

# Checks if the user calling a command has the right permissions by going
# through their list of roles and checking if any of them have the "Manage Role"
# permission enabled. Returns True if they do. False if they don't.
def canManageRoles(ctx):
    userRoles = ctx.message.author.roles
    for role in userRoles:
        if role.permissions.manage_roles == True:
            return True
    return False


            
