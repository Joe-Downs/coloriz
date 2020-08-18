import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def getLogLevel():
    logLevel = config["General"]["LogLevel"].upper()
    return logLevel

def getPrefix():
    prefix = config["Bot"]["CommandPrefix"]
    return prefix

def getToken():
    token = str(config["Bot"]["DiscordToken"])
    return token
