import threading
import socket
import signal
import mysql.connector
import hashlib

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()
exit_flag = False

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="chat_db"
    )
    mycursor = mydb.cursor()

    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                print(f"{addr} Disconnected!")
                continue  # Skip to the `finally` block to remove and close the connection

            elif msg.startswith("route_"):
                client_msg = msg.split(',')
                command = client_msg[0].replace("route_", "")

                if command == "register":
                    username = client_msg[1]
                    password = client_msg[2]

                    sql = "INSERT INTO users (name, password) VALUES (%s, %s)"
                    val = (username, hash_password(password))
                    mycursor.execute(sql, val)
                    mydb.commit()
    
                    mycursor.execute("SELECT id FROM users WHERE name = %s", (username, ))
                    row = mycursor.fetchone()
                    if row[0]:
                        user_id = row[0]
                        mycursor.execute("INSERT INTO sessions (user_id) VALUES (%s)", (user_id,))
                        mydb.commit()
                        authentication_successful = True
                    else:
                        authentication_successful = False

                    if authentication_successful:
                        reply = f"status:200,authenticated:{authentication_successful},user_id:{user_id}"
                    else:
                        reply = f"status:404,authenticated:{authentication_successful}"
                    conn.send(reply.encode(FORMAT))
                elif command == "login":
                    username = client_msg[1]
                    password = client_msg[2]

                    sql = "SELECT id FROM users WHERE name = %s AND password = %s"
                    val = (username, hash_password(password))
                    mycursor.execute(sql, val)
                    row = mycursor.fetchone()

                    if row:
                        user_id = row[0]
                        mycursor.execute("INSERT INTO sessions (user_id) VALUES (%s)", (user_id,))
                        mydb.commit()
                        authentication_successful = True
                    else:
                        authentication_successful = False

                    if authentication_successful:
                        reply = f"status:200,authenticated:{authentication_successful},user_id:{user_id}"
                    else:
                        reply = f"status:404,authenticated:{authentication_successful}"
                    conn.send(reply.encode(FORMAT))
                elif command == "logout":
                    user_id = client_msg[1]
                    
                    sql = "DELETE FROM sessions WHERE user_id = %s"
                    val = (user_id,)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    row = mycursor.fetchone()

                    if row[0]:
                        logout_successful = True
                    else:
                        logout_successful = False

                    if logout_successful:
                        reply = f"status:200,loggedout:{logout_successful},user_id:{user_id}"
                    else:
                        reply = f"status:404,loggedout:{logout_successful}"
                        
                    conn.send(reply.encode(FORMAT))
                elif command == "users":
                    sql = "SELECT users.id, users.name FROM users"
                    mycursor.execute(sql)
                    rows = mycursor.fetchall()
                    
                    if rows:
                        search_successful = True
                    else:
                        search_successful = False

                    if search_successful:
                        reply = f"status:200,{rows}"
                    else:
                        reply = f"status:404,user_found:{search_successful}"
                        
                    conn.send(reply.encode(FORMAT))
                elif command == "online_users":
                    sql = "SELECT users.id, users.name FROM users JOIN sessions ON users.id = sessions.user_id"
                    mycursor.execute(sql)
                    rows = mycursor.fetchall()
                    
                    if rows:
                        search_successful = True
                    else:
                        search_successful = False

                    if search_successful:
                        reply = f"status:200,{rows}"
                    else:
                        reply = f"status:404,online_found:{search_successful}"
                        
                    conn.send(reply.encode(FORMAT))
                elif command == "messages":
                    s_id = client_msg[1]
                    r_id = client_msg[2]

                    sql = """
                        SELECT *
                        FROM messages
                        WHERE (sender_id = %s AND receiver_id = %s)
                        OR (sender_id = %s AND receiver_id = %s)
                        ORDER BY id ASC;
                    """
                    mycursor.execute(sql, (s_id, r_id, r_id, s_id))
                    rows = mycursor.fetchall()
                                                    
                    if rows:
                        messages=[]
                        for message_id, sender_id, receiver_id, message in rows:
                            mycursor.execute("SELECT name FROM users WHERE id=%s", (sender_id,))
                            row = mycursor.fetchone()
                            messages.append((row[0], message))
                        print(messages)
                        reply = f"status:200, messages:{messages}"
                    else:
                        reply = "status:404, messages:none"
                    conn.send(reply.encode(FORMAT))
                elif command == "new_message":
                    sender_id = client_msg[1]
                    receiver_id = client_msg[2]
                    message = client_msg[3]
                    
                    print("Here: ",sender_id,"\n", receiver_id, "\n", message)
                    
                    sql = """
                        INSERT INTO messages (sender_id, receiver_id, message)
                        VALUES (%s, %s, %s);
                    """
                    mycursor.execute(sql, (sender_id, receiver_id, message))
                    mydb.commit()
                    if mycursor.rowcount:
                        reply = "status:200, message:"
                    else:
                        reply = "status:404"
                    conn.send(reply.encode(FORMAT))
                else:
                    print(f"Unknown command: {command}")
                    reply = "status:404, msg: Invalid command"
                    conn.send(reply.encode(FORMAT))

            else:
                print(f"[{addr}] {msg}")  # You can process other message types here

    except Exception as e:
        print(f"An error occurred with {addr}: {str(e)}")
        exception_stop()

    finally:
        with clients_lock:
            clients.remove(conn)
        mycursor.close()
        mydb.close()
        conn.close()

def start():
    global exit_flag
    print('[SERVER STARTED]!')
    server.listen()
    while not exit_flag:
        conn, addr = server.accept()
        with clients_lock:
            clients.add(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

def exception_stop():
    global exit_flag
    exit_flag = True
    with clients_lock:
        for conn in clients:
            conn.close()
    server.close()

def interrupt_stop(signal, frame):
    print("[!] Keyboard Interrupted!")
    with clients_lock:
        for conn in clients:
            conn.close()
    server.close()
    exit(0)

def hash_password(password):
    """Hashes a password using the SHA-256 algorithm."""
    hasher = hashlib.sha256()
    hasher.update(password.encode("utf-8"))
    hashed_password = hasher.hexdigest()
    return hashed_password

def verify_password(password, hashed_password):
    """Verifies if a password matches the stored hashed password."""
    return hashed_password == hash_password(password)

signal.signal(signal.SIGINT, interrupt_stop)
start()
