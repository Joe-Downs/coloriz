# Module meant to be run once to create and setup the database needed by the
# bot.

import sqlite3

# The database is created relative to where the command is called.
conn = sqlite3.connect("coloriz.db")
curs = conn.cursor()

# Shorthand string used in every table to create the sqlID column, which gives
# each row a unique ID that autoincrements whenever a row is inserted into the
# table. (To autoincrement it, NULL must be inserted into its column)
sqlID = "sqlID INTEGER PRIMARY KEY AUTOINCREMENT"

# Create the table for color history.
curs.execute(f"""
CREATE TABLE colorHistory ({sqlID}, userID INTEGER, serverID INTEGER, color
TEXT, timestamp TEXT, length INTEGER)""")

conn.commit()
conn.close()
