import socket
import time
import mysql.connector
import hashlib
import os



PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

connection = None
mydb = None



def connect():
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ADDR)
  
  return client

def send(client, msg):
  message = msg.encode(FORMAT)
  client.send(message)
  reply = client.recv(1024).decode(FORMAT)
  print("Server reply: ", reply)
    
def start():
  global connection
  global mydb
  
  print("Connecting to chat....")
  
  connection = connect()
  

start()
send(connection, "route_register, nati, 1432")
input()
send(connection, DISCONNECT_MESSAGE)
connection.close()