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

        frame1 = tk.LabelFrame(self.main_frame, text = 'Running processes', width = 1000, height = 400)
        frame1.grid(column = 0, row = 0, sticky='nsew')

        frame2 = tk.LabelFrame(self.main_frame, text='Docker logs', width = 1000, height = 400)
        frame2.grid(column = 1, row = 0, sticky = 'nswe')


        frame3 = tk.LabelFrame(self.main_frame, bg = 'green', text = 'Control panel', width = 1000, height = 400)
        frame3.grid(column = 0, row = 1, sticky='nswe')

        frame4 = tk.LabelFrame(self.main_frame, text = 'trending keywords', width = 1000, height = 400)
        frame4.grid(column = 1, row = 1, sticky='nswe')

        self.trending_keywords_list = tk.Listbox(frame4, width = 50)
        self.trending_keywords_list.pack(side = 'left', fill='y')

        self.trending_keywords_scrollbar = tk.Scrollbar(frame4)
        self.trending_keywords_scrollbar.pack(side = 'right', fill = 'y')

        self.trending_keywords_list.configure(yscrollcommand=self.trending_keywords_scrollbar.set)
        self.trending_keywords_scrollbar.configure(command = self.trending_keywords_list.yview)

        for _ in range(100):
            self.trending_keywords_list.insert('end', 'test')

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
        self.controller.start_scraping_trending_keywords()
    
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
    
    def add_trending_keywords(self, data):
        '''
        data format:
        keyword
        count
        date
        '''
        # date_string = data['date'].strftime("")
        date_string = data['date'].strftime('%m-%d-%Y %H:%M:%S')
        self.trending_keywords_list.insert('end', f"{date_string} | rank: {data['rank']} | keyword: {data['keyword']}")

    def clear_trending_keywords(self):
        self.trending_keywords_list.delete(0, 'end')

    def update_trending_keywords(self, keyword_list: list()):
        self.clear_trending_keywords()
        for item in keyword_list:
            self.add_trending_keywords(item)

    def update_scraping_keywords_index(self, index):
        # Highlight the scraping keyword
        self.trending_keywords_list.activate(index)

class AnotherPanel(Widget):
    def __init__(self, parent):
        Widget.__init__(self, parent)
        label = tk.Label(self.main_frame, text = 'Label 1')
        label.pack(side = 'top')