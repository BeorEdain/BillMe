# TODO: Literally everything.

import mysql.connector

credentials = []

with open("database_credentials", 'rt') as key:
    for item in key:
        credentials.append(str(item).strip())

mydb = mysql.connector.connect(
    host=credentials[0],
    user=credentials[1],
    password=credentials[2],
    database=credentials[3]
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE testDatabase")

# mycursor.execute("CREATE TABLE testTable (name VARCHAR(100), test2 VARCHAR(100))")

mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

# FOR NOW THIS IS THE MOST RUDAMENTARY MYSQL ACCESS EVER. NO JUDGEMENTS. Or do.
# That's fine.