import socket
import threading
import writer
import os
import csv #database table libary
from datetime import datetime #for timestamps]
from style import *
import time
HEADER = 64
PORT = 5057
FORMAT = "utf-8"
DISCONNECT_MESSAGE= "!DISCONNECTING!"
SERVER = "127.0.1.1"
ADDR = (SERVER, PORT)
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
except:
    print("Couldn't connect to server")
    exit()

"""
Header 64 chars
[current_date_time_length]
[msg_length]
Main body:
current_date_time
message

"""
def send(msg):
    global lost_connection
    if not lost_connection:
        try:
            true_current_date_time = str(time.time())
            current_date_time = str(datetime.now().strftime("%H:%M"))
            messages_to_send = [true_current_date_time,current_date_time,msg] #Add here everything you want to send in main body of packet
            messages_to_send_encoded = []
            lengths_encoded = []
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


def receive():
    global lost_connection,username,num_msg_received
    msg_recieved = ""
    while not lost_connection:
        if num_msg_received == 0 and msg_recieved == "reject username":
            username = "rejected"
        elif num_msg_received == 0 and msg_recieved != "":
            username = msg_recieved
            num_msg_received += 1
        elif msg_recieved != "":
            writer.print_next_line(msg_recieved) #print
            msg_recieved = ""
            num_msg_received += 1
        msg_recieved = client.recv(2048).decode(FORMAT)

lost_connection = False
username = ""
num_msg_received =0
thread= threading.Thread(target=receive, daemon=True)
thread.start()
try:
    try:
        send(input("Enter your username: "))
        while username == "" or username == "rejected":
            if username == "rejected":
                print("Username was rejected!")
                os.system("sleep 1")
                send(input("Enter your username: "))
                username = ""

        #send(input("What would you like to do? \n 1. Join a chat 2. Create a chat"))
    
        writer.start_terminal() # initiate 
        done = False
        while not done and not lost_connection:
            writer.reload_screen() # reload
            inputs_multiple = writer.get_input_queue() # retrive list of all inputs first -> oldest, last -> youngest ["1","2","3"]
            for input_ in inputs_multiple:
                if input_ == 'exit':
                    done = True
                    break
                else:
                    send(input_)
    except KeyboardInterrupt:
        pass

finally:
    if writer.is_initiated():
        writer.restore_terminal()
    if lost_connection:
        print("Connection was lost!")
    send(DISCONNECT_MESSAGE)
    lost_connection = True
    thread.join()
    if int(threading.active_count())-1 != 0:
        style_print("THREAD COUNT ON EXIT",BRIGHT_RED,f"{int(threading.active_count())-1}")
    else:
        style_print("THREAD COUNT ON EXIT",GREEN,f"{int(threading.active_count())-1}")
