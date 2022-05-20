import tkinter as tk
# from tkinter import ttk
from datetime import datetime

class Widget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.main_frame = tk.Frame(self, bg = '#272727', height = 1000, width = 2000)
        self.main_frame.grid(row=0, column=0, sticky='nswe')

class ControllPanel(Widget):

    def __init__(self, parent, controller):
        Widget.__init__(self, parent)

        self.controller = controller

        self.splash_container = controller._get_splash_container()

        frame1 = tk.LabelFrame(self.main_frame, text = 'Running processes', width = 1500, height = 400)
        frame1.grid(column = 0, row = 0, sticky='nsew')

        frame2 = tk.LabelFrame(self.main_frame, text='Docker logs', width = 500, height = 400)
        frame2.grid(column = 1, row = 0, sticky = 'nswe')

        frame3 = tk.LabelFrame(self.main_frame, bg = 'green', text = 'Control panel', width = 1500, height = 400)
        frame3.grid(column = 0, row = 1, sticky='nswe')

        self.listbox = tk.Listbox(frame1, width=100)

        self.listbox.pack(side = 'left', fill='both', expand = True)

        start_splash_button = tk.Button(frame2, text = 'start splash', command = self.start_splash)
        start_splash_button.pack()

        stop_splash_button = tk.Button(frame2, text = 'stop splash', command= self.stop_splash)
        stop_splash_button.pack()

        log_splash_button = tk.Button(frame2, text = 'clear logs', command= self.clear_log)
        log_splash_button.pack()

        start_scraper = tk.Button(frame2, text = 'start scraper', command = self.start_scraper) 
        start_scraper.pack()

        self.docker_running_status_label = tk.Label(frame2, text='Getting ready ... ')
        self.docker_running_status_label.pack(side = 'top')

        self.docker_status = None
        self.add_log('Checking splash container ...')
        
    def test_callback(self):
        print("test callback called")
    
    def start_scraper(self):
        self.controller._start_scraper_async()
    
    def toggle_docker_status(self, is_running):
        if is_running:
            self.docker_running_status_label.config(text = "Splash status: RUNNING")
            self.add_log("Splash container running")
        else:
            self.docker_running_status_label.config(text = "Splash status: NOT RUNNING")
            self.add_log("Splash container is not running")
    
    def start_splash(self):
        self.controller.start_splash()
    
    def stop_splash(self):
        self.controller.stop_splash()

    def clear_log(self):
        self.listbox.delete(0, 'end')

    def add_log(self, text):
        now = datetime.now()
        self.listbox.insert('end', f'{now.strftime("%m-%d-%Y : %H:%M:%S")} : {text}')
        self.listbox.see('end')

class AnotherPanel(Widget):
    def __init__(self, parent):
        Widget.__init__(self, parent)
        label = tk.Label(self.main_frame, text = 'Label 1')
        label.pack(side = 'top')