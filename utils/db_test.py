import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin"
)
cursor = mydb.cursor()

for x in cursor:
  print(x)