import socket
import threading
import writer
import os
import csv #database table libary
from datetime import datetime #for timestamps]
from style import *
import time
import hashlib
import getpass # for password entering

HEADER = 64
PORT = 5057
FORMAT = "utf-8"
DISCONNECT_MESSAGE= "!DISCONNECTING!"
SERVER = "127.0.1.1"
ADDR = (SERVER, PORT)
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(ADDR)
    client.settimeout(None)
except:
    print("Couldn't connect to server")
    exit()

"""
Header 64 chars
[length]
Main body:
current_date_time
message

"""
def auth(username,password,is_registered): #SEND PACKET WITH USERS PASSWORD AND USERNAME IN IT
    global lost_connection
    if not lost_connection:
        try:
            messages_to_send = [username,password,str(is_registered)] #Add here everything you want to send in main body of packet
            '''
            HEADER
            len(MAIN_BODY)
            
            MAIN BODY
            username \x00 password \x00 str(is_registered) ("True","False")
            '''
            messages_to_send_encoded = []
            for msg in messages_to_send:
                msg_encoded = msg.encode(FORMAT)
                messages_to_send_encoded.append(msg_encoded) 
            msg_to_send = b"\x00".join(messages_to_send_encoded)
            header_to_send = str(len(msg_to_send)).encode(FORMAT)
            header_to_send += b" " * (HEADER - len(header_to_send))
            #print("HEADER")
            #print(header_to_send.strip())
            #print("MAIN BODY")
            #print(messages_to_send)
            client.send(header_to_send)
            client.send(msg_to_send)
        except:
            lost_connection = True
def send(msg): #SEND PACKET WITH USER MSG IN IT
    global lost_connection
    if not lost_connection:
        try:
            true_current_date_time = str(time.time())
            current_date_time = str(datetime.now().strftime("%H:%M"))
            messages_to_send = [true_current_date_time,current_date_time,msg] #Add here everything you want to send in main body of packet
            '''
            HEADER
            len(MAIN_BODY)
            
            MAIN BODY
            true_current_date_time \x00 current_date_time \x00 msg
            '''
            messages_to_send_encoded = []
            for msg in messages_to_send:
                msg_encoded = msg.encode(FORMAT)
                messages_to_send_encoded.append(msg_encoded)
            msg_to_send = b"\x00".join(messages_to_send_encoded)
            header_to_send = str(len(msg_to_send)).encode(FORMAT)
            header_to_send += b" " * (HEADER - len(header_to_send))
            #print("HEADER")
            #print(header_to_send.strip())
            #print("MAIN BODY")
            #print(messages_to_send)
            client.send(header_to_send)
            client.send(msg_to_send)
        except:
            lost_connection = True


def receive(): #RECIVES NON STOP MESSAGES FROM SERVER
    global lost_connection,authed,cache
    
    msg_recieved = ""
    
    while not lost_connection:
        if authed == "waiting_for_response" and msg_recieved == "reject":
            authed = "rejected"
            msg_recieved = ""
        elif authed == "waiting_for_response" and msg_recieved == "accept":
            authed = "accepted"
            msg_recieved = ""
        elif msg_recieved != "":
            cache = cache +"\n"+ str(msg_recieved)
            writer.print_next_line(msg_recieved) #print
            msg_recieved = ""
        if msg_recieved == "":
            msg_recieved = client.recv(2048).decode(FORMAT)
lost_connection = False
username = ""
authed = "" #Variable that confirms auth
cache = ""
os.system("clear")
thread= threading.Thread(target=receive, daemon=True)
thread.start()

try:
    try:#TRIES TO START SERVER
        choice = writer.get_input_menu()
        if choice == 2:
            exit()
        if choice == 0:
            username,password = writer.login_menu()
            auth(username,password,"True")
        elif choice == 1:
           username,password = writer.register_menu()
           auth(username,password,"False")
        authed = "waiting_for_response"
        while (authed == "waiting_for_response" or authed == "rejected") and not lost_connection: #AUTH ATTEMPT FAILED
            if authed == "rejected":
                if choice == 0:
                    username,password = writer.login_menu("Wrong password or username!")
                    auth(username,password,"True")
                elif choice == 1:
                   username,password = writer.register_menu("Username was rejected")
                   auth(username,password,"False")
                authed = "waiting_for_response"
        writer.start_terminal(cache) # initiate msg terminal
        done = False
        while not done and not lost_connection: #SERVER LOOP
            writer.reload_screen() # reload
            inputs_multiple = writer.get_input_queue() # retrive list of all inputs first -> oldest, last -> youngest ["1","2","3"]
            for input_ in inputs_multiple:
                if input_ == 'exit':
                    done = True
                    break
                else:
                    send(input_)
    
    except KeyboardInterrupt:#USER REQUESTED EXIT
        pass

finally:
    if writer.is_initiated():
        writer.restore_terminal()
    if lost_connection:
        print("Connection was lost!")
    else:
        send(DISCONNECT_MESSAGE)
    lost_connection = True
    thread.join()
    if int(threading.active_count())-1 != 0:
        style_print("THREAD COUNT ON EXIT",BRIGHT_RED,f"{int(threading.active_count())-1}")
    else:
        style_print("THREAD COUNT ON EXIT",GREEN,f"{int(threading.active_count())-1}")
