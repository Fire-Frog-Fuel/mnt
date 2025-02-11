import socket
import threading
import os
from style import *
import re # lib for special formating of input? 
import csv 
from datetime import datetime 
import time
import hashlib
import json
def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()
HEADER = 64
PORT = 5057
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE= "!DISCONNECTING!"

'''
Yegor sends message

Clints are: Y, M, A
Y 123
  |  |  
  V  V
  M  A

  global_messages = all messages while server running
  local_messages = []
  ..
  global_messages send all previous together
  send them and they enter local_messages

  and now continiously we check all global_messages is different of local_messages
'''

def validate_string(s): #HELPS TO CHECK IF USERNAME IS VALID
    # Define the regex pattern
    pattern = r"^[a-zA-Z][a-zA-Z0-9_]*[a-zA-Z0-9]$"
    
    # Check if the string matches the pattern
    if re.fullmatch(pattern, s):
        # Check if underscores are only in the middle
        if "__" not in s and not s.startswith("_") and not s.endswith("_"):
            return True
    return False
    '''
    "hello_world"    # Valid
    "hello123"       # Valid
    "1hello"         # Invalid (starts with a number)
    "hello_"         # Invalid (ends with underscore)
    "hello__world"   # Invalid (double underscore)
    "hello world"    # Invalid (contains space)
    "helloWorld1"    # Valid
    '''
def verify_username(username): #CHECKS IF USERNAME IS VALID
    if all_usernames.count(username) == 0:
        if len(username) <= 20 and len(username) >= 3:
            return validate_string(username)
    return False

kill_all = False
all_connections = [] #Global variable keeping track of all current connections
all_usernames = [] #Global variable keeping of all usernames online
all_threads = [] #Global variable keeping track of all threads that are working rn
def sending_real_time(conn,addr,local_messages_sent): #SENDING MESSAGES TO SPECIFIC CLIENT
    while not kill_all:
        new_id = 0
        cursor = 0
        if len(Global_messages) > len(local_messages_sent):
            for item_id in range(cursor,len(Global_messages)):
                if Global_messages[:item_id] == local_messages_sent:
                    new_id = item_id
            cursor = new_id-5
            if cursor < 0:
                cursor = 0
            delta = Global_messages[new_id:]
            text = "\n".join(delta).encode(FORMAT)
            try:
                conn.send(text)    #real time sending
            except:
                if not kill_all:
                    WARNING("(sending_real_time): couldn't send message. Closing unused thread.")
                return 0
            local_messages_sent = Global_messages.copy()
def receive_data(conn): #WAITS UNTIL IT RECIVES DATA FROM USER
    recieve = []
    header_received = ''
    while recieve == [] and not kill_all:
        try:
            header_received = conn.recv(HEADER).decode(FORMAT) # RECIVING HERE TIMEOUT 1 sec
        except:
            pass
        if header_received:
            if header_received != '':
                main_body = conn.recv(int(header_received))
                recieve_ = main_body.split(b"\x00")
                for data in recieve_:
                    recieve.append(data.decode(FORMAT))
    #print(recieve) EASIER DEBUGGING WITH THIS
    return recieve
def handle_client(conn, addr): #HANDLES CLIENT
    global Global_messages, kill_all,all_usernames
    conn.settimeout(1) #TIMEOUT FOR RECIVING IF NO RECIVING IT WILL CRASH SO THERE IS TRY EXCEPT
    all_connections.append(conn)
    if kill_all:
        conn.close()
        return 0
    try:
        if not kill_all:
            style_print("NEW CONNECTION",GREEN,f" {addr} connected.")
        connected = True
        #AUTH loop
        auth = False
        while connected and not kill_all and not auth:
            try:
                username, password, is_registered = receive_data(conn)
                password = hash_string(password)
                if is_registered == "True":
                    with open("username_passwords.json", "r+") as file:
                        username_passwords = json.load(file)
                    if username_passwords.count([username,password]) == 1:
                        auth = True
                        conn.send("accept".encode(FORMAT))
                        if not kill_all:
                            print(f"{ORANGE}[LOGIN]{Style.RESET_ALL} Login successful! {username}")
                    else:
                        conn.send("reject".encode(FORMAT))
                        print(f"Rejected wrong password or username! {username} {password}")
                else:
                    with open("usernames.json", "r+") as file:
                        usernames = json.load(file)
                    if not verify_username(username):
                        conn.send("reject".encode(FORMAT))
                        if not kill_all:
                            print(f"Rejected this username didn't pass check [{username}]")
                    elif username in usernames:
                        conn.send("reject".encode(FORMAT))
                        if not kill_all:
                            print(f"Rejected this username exists [{username}]")
                    else:
                        usernames.append(username)
                        with open("usernames.json", "w+") as file:
                            json.dump(usernames, file)
                            
                        with open("username_passwords.json", "r+") as file:
                            username_passwords = json.load(file)
                        username_passwords.append([username,password])
                        with open("username_passwords.json", "w+") as file:
                            json.dump(username_passwords, file)
                        auth = True
                        conn.send("accept".encode(FORMAT))
                        print(f"[{ORANGE}REGISTER{Style.RESET_ALL}] New registered user: {username}")

            except Exception as e:
                if not kill_all:
                    ERROR(f"(handle_client auth) An error occured: {e}")
        if not kill_all:
            INFO(f"{username} joined with address: {addr}")
            style_print("CHAT",GREEN,f"{username} joined the conversation!")
            Global_messages.append(f"{username} joined the conversation!")
            try:
                local_messages_sent = []
                all_threads.append(threading.Thread(target=sending_real_time,args=(conn,addr,local_messages_sent), daemon=True))
                all_threads[-1].start()
            except Exception as e:
                if not kill_all:
                    ERROR(f"(handle_client adding to real time sending) An error occured: {e}")
                    
        #Main loop
        while connected and not kill_all and auth:
            try:
                true_time, timestamp, msg = receive_data(conn)
                msg = msg.strip()
                delta_time = time.time()-float(true_time)
                if msg == "":
                    pass
                elif msg == DISCONNECT_MESSAGE:
                    Global_messages.append(f"({timestamp})  {username} left the conversation!")
                    if not kill_all:
                       style_print("CHAT",GREEN,f"({timestamp})  {username} left the conversation!")
                else:
                    if not kill_all:
                        style_print("CHAT",GREEN,f"({timestamp})  [{username}] {msg} ({delta_time})")
                    Global_messages.append(f"({timestamp})  [{username}] {msg}") # sending here
                    
            except Exception as e:
                if not kill_all:
                    ERROR(f"(handle_client loop) An error occured: {e}")
            
    finally:
        try:
            all_usernames.remove(username)
        except Exception:
            pass
        try:
            thread.join("")
        except Exception:
            pass
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()
        all_connections.remove(conn)
def start(): #START SERVER
    global server,kill_all,all_connections
    server.listen()
    if not kill_all:
        style_print("LISTENING",GREEN,f"Server is listening on {SERVER}:{PORT}")
    while not kill_all:
        conn,addr = server.accept()
        all_threads.append(threading.Thread(target=handle_client, args=(conn,addr),daemon=True))
        all_threads[-1].start()
        if not kill_all:
            os.system("sleep 0.2")
            style_print("THREAD COUNT:",GREEN,f"{int(threading.active_count())-1}")
            style_print("ACTIVE CONNECTIONS:",GREEN,f"{len(all_connections)}")
os.system("clear")

try: #BINDS PORT
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)
except Exception as e:
    ERROR(f"An error occured on start: {e}")
    if str(e) == "[Errno 98] Address already in use":
        print(f"\nInstances taking {PORT} port: ")
        os.system(f"lsof -i:{PORT}")
        print("Kill them? (y/n)")
        y_n = input("> ")
        if y_n == "y":
            os.system(f"lsof -t -i:{PORT} | xargs kill -9")
            
            TIMEOUT = 3 # in seconds.  minimum value -> 1 
            print(f"\rLeft {TIMEOUT} seconds till restart",end="\r")
            os.system("sleep 1")
            for seconds in range(TIMEOUT-1,0,-1):
                print(f"Left {seconds} seconds till restart",end="\r")
                os.system("sleep 1")
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind(ADDR)
                os.system("clear")
            except Exception as e:
                ERROR(f"An error occured on start: {e}")
                exit()
        else:
            exit()
    else:
        exit()
try: #STARTS SERVER
    Global_messages = []
    style_print("STARTING",GREEN, "Server is starting...")
    start()
    server.close()
except KeyboardInterrupt: #USER REQUESTED EXIT
    print("\r"+"    ")
    INFO("\rServer shutdown requested by user.")
    print("Bye!")
    
finally: #NO MATTER WHAT SHUT DOWN SERVER
    print(ORANGE+"""
=================
[Stopping Server]
================="""+Style.RESET_ALL)
    kill_all = True
    for conn in all_connections: #CLOSE CONNECTIONS
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()
    os.system("sleep 1")
    server.close()
    os.system("sleep 1")
    for thread in all_threads:
        try:
            thread.join()
        except:
            pass
    if int(threading.active_count())-1 != 0:
        style_print("THREAD COUNT ON EXIT",BRIGHT_RED,f"{int(threading.active_count())-1}")
    else:
        style_print("THREAD COUNT ON EXIT",GREEN,f"{int(threading.active_count())-1}")