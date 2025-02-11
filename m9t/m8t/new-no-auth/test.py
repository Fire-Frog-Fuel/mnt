import writer
import os
writer.start_terminal() # initiate 
writer.change_input_msg("Enter text:")
while True:
    writer.reload_screen() # reload
    a = writer.get_input_queue() # retrive list of all inputs first -> oldest, last -> youngest
    if a != []:
        writer.print_next_line(a)
    if a == ['cls']:
        writer.clear_screen() #clear_screen
    if a == ['exit']:
        writer.restore_terminal() #exit
        break
