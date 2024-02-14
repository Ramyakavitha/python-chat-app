import socket
import time
import mysql.connector
import hashlib
import os
import ast
import sys


PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
connection = None



def connect():
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ADDR)
  client.setblocking(True)
  return client


def send(client, msg):
  message = msg.encode(FORMAT)
  client.send(message)
  if(msg != DISCONNECT_MESSAGE):
    reply = client.recv(1024).decode(FORMAT)
    return reply
  
def start():
  global connection
  
  print("Connecting to chat....")
  
  connection = connect()
  main_menu()

def main_menu():
  os.system('cls' if os.name == 'nt' else 'clear')
  
  print("Welcome to the Chat Application!")
  print("1. Login")
  print("2. Register")
  print("3. Exit")

  choice = input("\nPlease choose an option: ")
  if choice == "1":
    login_menu()
  elif choice == "2":
    registration_menu()
  elif choice == "3":
    print("Exiting...")
    send(connection, DISCONNECT_MESSAGE)
    connection.close()
    sys.exit()
  else:
    print("Invalid choice. Please try again.")
    main_menu()    

def registration_menu():
  print("\n**Registration**")
  username = input("1. Enter username: ")
  password = input("2. Enter password: ")  

  if len(username) > 0 and len(password) > 0:
    reply = send(connection, "route_register,"+username+","+password)  
    reply = reply.split(',')
    if reply[0].find("200") != -1:
      print("registering....")
      time.sleep(1)
      user_id = reply[2].replace("user_id:", "")
      chat_menu(user_id)
    else:
      print("Invalid username or password. Please try again.")
      registration_menu()
  
  print("\n3. Back to main menu")  # Add option to return to main menu
  
  input("\nBack to main menu")
  main_menu()

def login_menu():
  print("\n**Login**")
  username = input("1. Enter username: ")
  password = input("2. Enter password: ")  
  
  if len(username) > 0 and len(password) > 0:
    reply = send(connection, "route_login,"+username+","+password)  
    reply = reply.split(',')
    if reply[0].find("200") != -1:
      print("loggin....")
      time.sleep(.5)
      user_id = reply[2].replace("user_id:", "")
      chat_menu(user_id)
    else:
      print("Invalid username or password. Please try again.")
      login_menu()

  input("\nBack to main menu")
  main_menu()
  
def chat_menu(user_id):
  os.system('cls' if os.name == 'nt' else 'clear')
  
  print("\n**Chat Interface**")
  print("1. List online users")
  print("2. Choose a user to chat with")
  print("3. Logout")

  choice = input("\nPlease choose an option: ")
  if choice == "1":
    list_online_users(user_id)
  elif choice == "2":
    chat_with_user(user_id)
  elif choice == "3":
    reply = send(connection, "route_logout,"+user_id) 
    reply = reply.split(',')
    if reply[0].find("200") != -1:
      main_menu()
      
def list_online_users(my_id):
    reply = send(connection, "route_online_users") 
    
    if reply.find("200") != -1:
      reply = reply.replace("status:200,", "")
      reply = ast.literal_eval(reply)
      if len(reply) == 1:
        print("\nNo users are currently online.")
      else:
        print("\n\nUsers online....\n")
        for index, row in enumerate(reply):
          id, name = row
          if str(id) != str(my_id):
            print(f"{index+1} - {name}")
    input()
    chat_menu(my_id)

def chat_with_user(my_id):
  reply = send(connection, "route_users") 
    
  if reply.find("200") != -1:
    reply = reply.replace("status:200,", "")
    reply = ast.literal_eval(reply)
    for index, row in enumerate(reply):
      user_id, name = row
      if str(user_id) != str(my_id):
        print(f"{user_id} - {name}")
      
    user_ids = [row[0] for row in reply if str(row[0]) != str(my_id)]
    user_id = input("\n\nEnter the user id to chat with: ")
    if int(user_id) not in user_ids:
        print("\nInvalid user id. Please try again.")
        chat_with_user(my_id)
    else:
        show_chat(my_id, user_id)
  else:
    print("\nThere are no users on the platform.")
    time.sleep(2)
    chat_menu(my_id)
  
def show_chat(my_id, user_id):
  while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    reply = send(connection, "route_messages,"+my_id+","+user_id)
    if reply.find("status:200") != -1:
      reply = reply.replace("status:200, messages:", "")
      reply = ast.literal_eval(reply)
      for index, row in enumerate(reply):
        name, message = row
        print(f"{name}:   {message}")
    
    new_msg = input("Enter message(enter r to refresh chat, q to exit chat): ")
    if new_msg.lower() == "q":
      chat_menu(my_id)
      break
    elif new_msg.lower() == "r":
      continue
    else:
      reply = send(connection, "route_new_message,"+my_id+","+user_id+","+new_msg)
      os.system('cls' if os.name == 'nt' else 'clear')
      if reply != "status:200":
        print("Error during chat...")
        time.sleep(1)
        chat_menu(my_id)
      
def hash_password(password):
  """Hashes a password using the SHA-256 algorithm."""
  hasher = hashlib.sha256()
  hasher.update(password.encode("utf-8"))
  hashed_password = hasher.hexdigest()
  return hashed_password

def verify_password(password, hashed_password):
  """Verifies if a password matches the stored hashed password."""
  return hashed_password == hash_password(password)

start()