import threading
import curses
import os
import time
from style import *

user_input = ""
running_input = False
user_input_queue = []
cache = ""
LINE_CUT = 50
stdscr_ = ""
old_cache = "."
old_user_input = "."
reload_done = True
is_exit = False
input_msg = ">"
all_threads = []
state = "Stopped"
done = False
def change_input_msg(new_msg=str):
    global input_msg
    input_msg = new_msg
def clear_screen():
    global cache
    cache = ""
    reload_screen()
def reload_screen():
    global user_input,done,running_input,cache,LINE_CUT,stdscr_
    global old_cache, old_user_input, height_,width_,start_time,reload_done
    if reload_done:
        if stdscr_ == "":
            return None
        reload_done = False
        stdscr = stdscr_
        height, width = stdscr.getmaxyx()
        if (height > 5 and width > 40):
            if done:
                done = False
                user_input_queue.append(f"{user_input}")
                #print_next_line(user_input)
                user_input = ""
            if old_cache != cache or old_user_input != user_input or height_ != height or width_ != width:
                text_to_print = cut_cache(stdscr,LINE_CUT)
                try:
                    if text_to_print != "":
                        stdscr.clear()
                        stdscr.addstr(text_to_print)
                        stdscr.refresh()
                        old_cache = cache
                        old_user_input = user_input
                        start_time = time.time()
                        height_, width_ = height, width
                    else:
                        height, width = stdscr.getmaxyx()
                        curses.can_change_color()
                        curses.init_color(10, 1000, 500, 0)
                        curses.init_pair(5, 10, curses.COLOR_BLACK)
                        stdscr.clear()
                        string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
                        stdscr.addstr(f"{string_print}",curses.color_pair(5))
                        stdscr.refresh()
                except:
                    height, width = stdscr.getmaxyx()
                    curses.can_change_color()
                    curses.init_color(10, 1000, 500, 0)
                    curses.init_pair(5, 10, curses.COLOR_BLACK)
                    stdscr.clear()
                    string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
                    stdscr.addstr(f"{string_print}",curses.color_pair(5))
                    stdscr.refresh()
            stdscr.refresh()
            height_, width_ = height, width
            stdscr_ = stdscr
        else:
            height, width = stdscr.getmaxyx()
            curses.init_color(10, 1000, 500, 0)
            curses.init_pair(5, 10, curses.COLOR_BLACK)
            stdscr.clear()
            string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
            stdscr.addstr(f"{string_print}",curses.color_pair(5))
            stdscr.refresh()
        reload_done = True
def restore_terminal():
    global is_exit,state
    is_exit = True
    for thread in all_threads:
        thread.join()
    os.system("clear")
    try:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    except:
        pass
    os.system("reset")
    state = "Stopped"
    is_exit = False
def cut_cache(stdscr,lines=20):
    global cache,input_msg
    cache_lines = cache.split("\n")
    cache_lines.append(f"{input_msg} {user_input}")
    total_amount = len(cache_lines)
    stdscr.refresh()
    height, width = stdscr.getmaxyx()
    if height < lines:
        lines = height-1
    i =0
    while i < len(cache_lines):
        line = cache_lines[i]
        if len(cache_lines[i]) > width-1:
            cache_lines.insert(i,cache_lines[i][:width-1])
            cache_lines[i+1] = cache_lines[i+1][width-1:]
            total_amount += 1
        i += 1
    #while total_amount < lines:
    #    total_amount += 1
    if total_amount >= lines:
        cache_ = "\n".join(cache_lines[len(cache_lines)-lines:])
    else:
        cache_ = "\n".join(cache_lines)
    return cache_
def print_same_line(text:str):
    global cache 
    cache = cache + str(text)
    reload_screen()
def print_next_line(text:str):
    global cache 
    cache = cache +"\n"+ str(text)
    reload_screen()
def DONOTUSETHISget_input(stdscr): #regular msg
    global user_input,done
    global stdscr_
    global user_input,done,running_input,cache,LINE_CUT,height_, width_,start_time, is_exit,all_threads
    start_time = time.time()
    height_, width_ = stdscr.getmaxyx()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    stdscr.timeout(500)
    stdscr_ = stdscr
    while not is_exit:
        try:
            key = stdscr.getkey()
        except:
            key = -1
        if key == -1:
            pass
        elif key == '\n':
            if user_input != "":
                done = True
            reload_screen()
                #os.system("sleep 0.1") #To not cause any issues with other thread.
        elif key == "KEY_BACKSPACE":
            user_input = user_input[:-1]
            reload_screen()
        elif key == "KEY_DC": # POSSIBLITY TO ADD CURSOR BUT IT'S NOT GONNA BE EASY.
            pass
        elif key == "KEY_DOWN":
            pass
        elif key == "KEY_UP":
            pass
        elif "KEY" in key:
            pass
        elif key == "	":
            pass
        else:
            user_input_ = user_input + key
            if not done and user_input_.strip() != "":
                user_input = user_input + key
                reload_screen()
def get_input_menu():
    choice = ""
    while choice == "":
        try:
            choice = curses.wrapper(DONOTUSETHISget_input_menu)
        except:
            pass
    curses.curs_set(1)
    return choice
global message_login_global
def login_menu(message_login=""):
    global message_login_global
    message_login_global = message_login
    username= ""
    while username == "":
        try:
            username,password = curses.wrapper(DONOTUSETHISget_login_menu)
        except:
            pass
    return username,password
message_register_global = ""
def register_menu(message_register=""):
    global message_register_global
    message_register_global = message_register
    username= ""
    while username == "":
        try:
            username,password = curses.wrapper(DONOTUSETHISget_register_menu)
        except:
            pass
    return username,password
def print_login(stdscr,username,password,choice,lines):
    curses.start_color()
    curses.cbreak()
    curses.noecho()
    curses.init_color(10, 1000, 500, 0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, 10, curses.COLOR_BLACK)
    height, width = stdscr.getmaxyx()
    login_or_register = "Login"
    if (height > 5 and width > 45):
        login_register = " "*(width//2-len(login_or_register)//2)+login_or_register
        stdscr.clear()
        stdscr.addstr(f"{login_register}\n\n",curses.color_pair(1))
        stdscr.addstr(f"{lines[0]} ",curses.color_pair(4))
        if choice == 0:
            stdscr.addstr(f"{username}_\n",curses.color_pair(2))
        else:
            stdscr.addstr(f"{username}\n",curses.color_pair(2))
        password_hidden = "*"*len(password)
        stdscr.addstr(f"{lines[1]} ",curses.color_pair(4))
        if choice == 1:
            stdscr.addstr(f"{password_hidden}_\n",curses.color_pair(2))
        else:
            stdscr.addstr(f"{password_hidden}\n",curses.color_pair(2))
        stdscr.addstr(f"{message_login_global}\n",curses.color_pair(5))
        stdscr.move(choice+2, len([f"{lines[0]} {username}",f"{lines[1]} {password_hidden}"][choice]))
        stdscr.refresh()
        update_required = False
    else:
        height, width = stdscr.getmaxyx()
        curses.init_color(10, 1000, 500, 0)
        curses.init_pair(5, 10, curses.COLOR_BLACK)
        stdscr.clear()
        string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
        stdscr.addstr(f"{string_print}",curses.color_pair(5))
        stdscr.refresh()

def print_reg(stdscr,username,password,password_confirm,choice,lines,not_same,empty_string):
    curses.start_color()
    curses.cbreak()
    curses.noecho()
    curses.init_color(10, 1000, 500, 0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, 10, curses.COLOR_BLACK)
    height, width = stdscr.getmaxyx()
    login_or_register = "Register"
    if (height > 7 and width > 53):
        login_register = " "*(width//2-len(login_or_register)//2)+login_or_register
        stdscr.clear()
        stdscr.addstr(f"{login_register}\n\n",curses.color_pair(1))
        stdscr.addstr(f"{lines[0]} ",curses.color_pair(4))
        if choice == 0:
            stdscr.addstr(f"{username}_\n",curses.color_pair(2))
        else:
            stdscr.addstr(f"{username}\n",curses.color_pair(2))
        password_hidden = "*"*len(password)
        password_confirm_hidden = "*"*len(password_confirm)
        stdscr.addstr(f"{lines[1]} ",curses.color_pair(4))
        if choice == 1:
            stdscr.addstr(f"{password_hidden}_\n",curses.color_pair(2))
        else:
            stdscr.addstr(f"{password_hidden}\n",curses.color_pair(2))
        stdscr.addstr(f"{lines[2]} ",curses.color_pair(4))
        if choice == 2:
            stdscr.addstr(f"{password_confirm_hidden}_\n")
        else:
            stdscr.addstr(f"{password_confirm_hidden}\n")
        if empty_string:
            stdscr.addstr(f"One or more fields were left empty!\n",curses.color_pair(5))
        elif not_same:
            stdscr.addstr(f"Password and password confirm are not the same!\n",curses.color_pair(5))
        if message_register_global != "":
            stdscr.addstr(f"{message_register_global}\n",curses.color_pair(5))
        stdscr.move(choice+2, len([f"{lines[0]} {username}",f"{lines[1]} {password_hidden}",f"{lines[2]} {password_confirm_hidden}"][choice]))
        stdscr.refresh()
    else:
        height, width = stdscr.getmaxyx()
        curses.init_color(10, 1000, 500, 0)
        curses.init_pair(5, 10, curses.COLOR_BLACK)
        stdscr.clear()
        string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
        stdscr.addstr(f"{string_print}",curses.color_pair(5))
        stdscr.refresh()
def print_menu(stdscr,choice,choices):
    curses.start_color()
    curses.cbreak()
    curses.noecho()
    curses.init_color(10, 1000, 500, 0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, 10, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
    height, width = stdscr.getmaxyx()
    login_or_register = "Menu"
    curses.curs_set(0)
    if (height > 5 and width > 12):
        login_register = " "*(width//2-len(login_or_register)//2)+login_or_register
        stdscr.clear()
        stdscr.addstr(f"{login_register}\n\n",curses.color_pair(1))
        for i in range(0,len(choices)):
            if i == choice:
                stdscr.addstr(f"> {choices[i]}\n",curses.color_pair(6))
            else:
                stdscr.addstr(f"  {choices[i]}\n",2)
        stdscr.refresh()
    else:
        height, width = stdscr.getmaxyx()
        curses.init_color(10, 1000, 500, 0)
        curses.init_pair(5, 10, curses.COLOR_BLACK)
        stdscr.clear()
        string_print = "\n"*(height//2)+" "*((width//2)-len("Not enough space")//2)+"Not enough space"
        stdscr.addstr(f"{string_print}",curses.color_pair(5))
        stdscr.refresh()
def DONOTUSETHISget_login_menu(stdscr): #login menu
    global user_input,done
    global stdscr_
    global user_input,done,running_input,cache,LINE_CUT,height_, width_,start_time, is_exit,all_threads,message_login_global
    start_time = time.time()
    height_, width_ = stdscr.getmaxyx()
    curses.cbreak()
    curses.noecho()
    curses.start_color()
    
    stdscr.keypad(True)
    stdscr.timeout(500)
    stdscr_ = stdscr
    lines = ["Username:","Password:"]
    username = ""
    password = ""
    choice = 0
    height, width = stdscr.getmaxyx()
    print_login(stdscr,username,password,choice,lines)
    update_required = False
    height, width = stdscr.getmaxyx()
    while not is_exit:
        height, width = stdscr.getmaxyx()
        if (height,width) != (height_, width_):
            update_required = True
            height_, width_ = height, width
        if update_required:
            print_login(stdscr,username,password,choice,lines)
        try:
            key = stdscr.getkey()
        except:
            key = -1
        if key == -1:
            pass
        elif key == "KEY_BACKSPACE":
            if choice == 0:
                username = username[:-1]
            elif choice == 1:
                password = password[:-1]
            update_required = True
        elif key == '\n':
            choice += 1
            if choice == 2:
                return username,password
            update_required = True
        elif key == "KEY_DOWN":
            choice += 1
            if len(lines) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(lines)-1
            update_required = True
        elif key == "KEY_UP":
            choice -= 1
            if len(lines) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(lines)-1
            update_required = True
        elif "KEY" in key:
            pass
        else:
            height_, width_ = stdscr.getmaxyx()
            if choice == 0:
                if len(username) < 20 and len(f"{lines[0]} {username}_\n")<width_: 
                    username = username + key
            elif choice == 1:
                if len(password) < 32 and len(f"{lines[1]} {password}_\n") < width_: 
                    password = password + key
            update_required = True
def DONOTUSETHISget_register_menu(stdscr): #register menu
    global user_input,done
    global stdscr_
    global user_input,done,running_input,cache,LINE_CUT,height_, width_,start_time, is_exit,all_threads
    start_time = time.time()
    height_, width_ = stdscr.getmaxyx()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    stdscr.timeout(500)
    stdscr_ = stdscr
    login_register = "Register"
    lines = ["Username:","Password:", "Confirm password:"]
    username = ""
    password = ""
    password_confirm = ""
    stdscr.clear()
    choice = 0
    update_required = False
    not_same = False
    empty_string = False
    height, width = stdscr.getmaxyx()
    height_, width_ = stdscr.getmaxyx()
    print_reg(stdscr,username,password,password_confirm,choice,lines,not_same,empty_string)
    while not is_exit:
        if (height,width) != (height_, width_):
            update_required = True
            height_, width_ = height, width
        if update_required:
            print_reg(stdscr,username,password,password_confirm,choice,lines,not_same,empty_string)
        try:
            key = stdscr.getkey()
        except:
            key = -1
        if key == -1:
            pass
        elif key == "KEY_BACKSPACE":
            if choice == 0:
                username = username[:-1]
            elif choice == 1:
                password = password[:-1]
            elif choice == 2:
                password_confirm = password_confirm[:-1]
            update_required = True
        elif key == '\n':
            choice += 1
            if choice == 3:
                if password != password_confirm:
                    password_confirm = ""
                    choice = 2
                    not_same = True
                elif password == "" or username == "":
                    choice = 2
                    empty_string = True
                else:
                    return username,password
            update_required = True
        elif key == "KEY_DOWN":
            choice += 1
            if len(lines) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(lines)-1
            update_required = True
        elif key == "KEY_UP":
            choice -= 1
            if len(lines) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(lines)-1
            update_required = True
        elif "KEY" in key:
            pass
        else:
            height_, width_ = stdscr.getmaxyx()
            if choice == 0:
                if len(username) < 20 and len(f"{lines[0]} {username}_\n")<width_: 
                    username = username + key
            elif choice == 1:
                if len(password) < 32 and len(f"{lines[1]} {password}_\n") < width_: 
                    password = password + key
            elif choice == 2:
                if len(password_confirm) < 32 and len(f"{lines[2]} {password_confirm}_\n") < width_: 
                    password_confirm = password_confirm + key
            not_same = False
            empty_string = False
            update_required = True
def DONOTUSETHISget_input_menu(stdscr): #input menu
    global user_input,done
    global stdscr_
    global user_input,done,running_input,cache,LINE_CUT,height_, width_,start_time, is_exit,all_threads
    start_time = time.time()
    height_, width_ = stdscr.getmaxyx()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    stdscr.timeout(500)
    stdscr_ = stdscr
    stdscr.clear()
    choices = ["Login","Register","Exit"]
    choice = 0
    print_menu(stdscr,choice,choices)
    update_required = False
    height, width = stdscr.getmaxyx()
    height_, width_ = stdscr.getmaxyx()
    while not is_exit:
        height, width = stdscr.getmaxyx()
        if (height,width) != (height_, width_):
            update_required = True
            height_, width_ = height, width
        if update_required:
            print_menu(stdscr,choice,choices)
            update_required = False
        try:
            key = stdscr.getkey()
        except:
            key = -1
        if key == -1:
            pass
        elif key == '\n':
            return choice
        elif key == "KEY_DOWN":
            choice += 1
            if len(choices) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(choices)-1
            stdscr.clear()
            update_required = True
        elif key == "KEY_UP":
            choice -= 1
            if len(choices) <= choice:
                choice = 0
            if 0 > choice:
                choice = len(choices)-1
            update_required = True
def menu():
    global user_input,done,running_input,cache,LINE_CUT,stdscr_
    global old_cache, old_user_input, height_,width_,start_time,reload_done
    if reload_done:
        if stdscr_ == "":
            return None
        reload_done = False
        stdscr = stdscr_
        interval = 1 / 30 # Update screen 30 times per second
        height, width = stdscr.getmaxyx()
        if done:
            done = False
            user_input_queue.append(f"{user_input}")
            #print_next_line(user_input)
            user_input = ""
        if old_cache != cache or old_user_input != user_input or height_ != height or width_ != width:
            text_to_print = cut_cache(stdscr,LINE_CUT)
            stdscr.clear()
            stdscr.addstr(text_to_print)
            stdscr.refresh()
            old_cache = cache
            old_user_input = user_input
            start_time = time.time()
            height_, width_ = height, width
        elapsed_time = time.time() - start_time
        if elapsed_time < interval:
            start_time = time.time()
            height, width = stdscr.getmaxyx()
            stdscr.refresh()
        height_, width_ = height, width
        stdscr_ = stdscr
        reload_done = True
def start_terminal(cache_=""):
    global done,user_input,cache,all_threads,state
    cache = cache_
    done = False
    user_input = ""
    all_threads.append(threading.Thread(target=curses.wrapper, args=(DONOTUSETHISget_input,), daemon=True))
    all_threads[-1].start()
    state = "Running"
def is_initiated():
    global state
    return state == "Running"
def get_input_queue():
    global user_input_queue
    user_input_queue_ = user_input_queue.copy()
    user_input_queue = []
    return user_input_queue_
