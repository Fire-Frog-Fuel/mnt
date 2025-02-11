import threading
import curses
import os
import time


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
def restore_terminal():
    global is_exit,state
    is_exit = True
    for thread in all_threads:
        thread.join()
    os.system("clear")
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    os.system("reset")
    state = "Stopped"
def cut_cache(stdscr,lines=20):
    global cache,input_msg
    cache_lines = cache.split("\n")
    total_amount = len(cache_lines)+1
    stdscr.refresh()
    height, width = stdscr.getmaxyx()
    if height < lines:
        lines = height-1
    for line in cache_lines:
        if len(line) > width:
            total_amount += int(len(line)//width)
    while total_amount < lines:
        cache_lines.append("")
        total_amount += 1
    cache_lines.append(f"{input_msg} {user_input}")
    if total_amount > lines:
        cache_ = "\n".join(cache_lines[total_amount-lines:])
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
def DONOTUSETHISget_input(stdscr):
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
        elif key == "KEY_RIGHT":
            pass
        elif key == "KEY_LEFT":
            pass
        elif "KEY" in key:
            pass
        else:
            if not done:
                user_input = user_input + key
                reload_screen()
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
