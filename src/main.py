from tkinter import *
import time
from datetime import datetime

global time_label
global milisec_label

def button_callback():
    print("Clicked hello")

def update_time():
    time_label.config(text=time.strftime('%H: %M: %S'))
    time_label.after(1000, update_time )

def update_milliseconds():
    milisec_label.config(text = datetime.now())
    milisec_label.after(1, update_milliseconds )

ws = Tk()
ws.title("Sample ")
ws.geometry("800x600")

time_label =  Label(
    ws,
    text=time.strftime('%H: %M: %S'),
    font=21,
    padx = 10,
    pady = 5,
)

milisec_label = Label(
    ws,
    text = time.strftime('%f'),
    font = 21,
    padx = 10,
    pady = 5
)

milisec_label.pack()

time_label.pack(expand=True)
ws.update()

button = Button(
    ws,
    font = 21,
    text="Hello",
    command = button_callback
)

button.pack()

update_time()
update_milliseconds()

ws.mainloop()