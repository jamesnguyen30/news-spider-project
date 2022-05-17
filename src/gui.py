import tkinter as tk
from screens.widgets import ControllPanel, AnotherPanel
from screens.windows import NewWindow
from multiprocessing import Pool 
from collector.collector import NewsCollector
from utils.docker_utils import SplashContainer
import os
import time


class MenuBar(tk.Menu):

    def __init__(self, parent):

        tk.Menu.__init__(self, parent)

        menu1 = tk.Menu(self, tearoff=0)
        menu1.add_command(label = 'Control Panel', command = lambda: parent.show_controll_panel())
        menu1.add_command(label = 'Another Panel', command = lambda: parent.show_another_panel())
        menu1.add_command(label = 'Option 3', command = lambda: print("Menu 1 Option 3 clicked"))
        menu1.add_separator()
        menu1.add_command(label = 'Option 4', command = lambda: print("Menu 1 Option 4 clicked"))

        self.add_cascade(label = "Menu 1", menu = menu1)

        menu2 = tk.Menu(self, tearoff=0)
        menu2.add_command(label = 'Option 1', command = lambda: print("Menu 2 Option 1 clicked"))
        menu2.add_command(label = 'Option 2', command = lambda: print("Menu 2 Option 2 clicked"))
        menu2.add_command(label = 'Option 3', command = lambda: print("Menu 2 Option 3 clicked"))
        menu2.add_separator()
        menu2.add_command(label = 'Option 4', command = lambda: print("Menu 2 Option 4 clicked"))

        self.add_cascade(label = "Menu 2", menu = menu2)


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.main_frame = tk.Frame(self, bg = '#272727', height = 1000, width = 2000)
        self.main_frame.pack_propagate(0)
        self.main_frame.pack(fill='both', expand = 'true')
        self.main_frame.grid_columnconfigure(0, weight = 1)
        self.main_frame.grid_rowconfigure(0, weight = 1)

        menubar = MenuBar(self)
        tk.Tk.config(self, menu = menubar)

        #init news collector
        self.news_collector = NewsCollector()
        #init splash container 
        self.splash_container = SplashContainer()

        self.splash_logs = list()

        self.show_controll_panel()

    def show_controll_panel(self):
        print('shoing control panel')
        self.controll_panel = ControllPanel(self.main_frame, self)
        self._show_widget(self.controll_panel)
        self.controll_panel.test_callback()
    
    def show_another_panel(self):
        print("showing another panel")
        w = AnotherPanel(self.main_frame)
        self._show_widget(w)
    
    def _show_widget(self, widget):
        widget.grid(row = 0, column = 0, sticky = 'nsew')
        widget.tkraise()

    def _start_scraper(self):
        pool_data = [ 
            self.news_collector.get_cnn_spider_data('apple', 'business', start_date = 'today', days_from_start_date=5), 
            self.news_collector.get_cnn_spider_data('tesla', 'business', start_date = 'today', days_from_start_date=5), 
        ]

        with Pool() as pool:
            res = pool.map(self.news_collector.start_cnn_search, pool_data)
        
        print(f"Completed processes with code {res}")
    
    def _add_log_to_controll_panel(self, text):
        self.controll_panel.add_log(text)
    
    def task_done(self, result):
        self._add_log_to_controll_panel(f'[ DONE ] {str(result)}')

    def _start_scraper_async(self):
        print("starting scrapers")
        pool_data = [
            self.news_collector.get_cnn_spider_data('apple', 'business', start_date = 'today', days_from_start_date=5), 
            self.news_collector.get_cnn_spider_data('tesla', 'business', start_date = 'today', days_from_start_date=5), 
        ]

        pool = Pool()
    
        for data in pool_data:
            self._add_log_to_controll_panel(f'[ CNN Spider ],args: {str(data)}')
            pool.apply_async(self.news_collector.start_cnn_search, (data,), callback=self.task_done)
        
        pool.close()
        print("end scraper")

    def _get_splash_container(self):
        return self.splash_container
    
    def _get_collector(self):
        return self.news_collector
        

if __name__ == '__main__':
    root = MyApp()
    root.title('My app')
    root.mainloop()
