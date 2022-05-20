import tkinter as tk
from screens.widgets import ControllPanel, AnotherPanel
from screens.windows import NewWindow
from multiprocessing import Pool 
from collector.collector import NewsCollector
from utils.docker_utils import SplashContainer
import subprocess
import pathlib
import os
from datetime import datetime

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
    CWD = pathlib.Path(__file__).parent.absolute()
    TRENDING_KEYWORDS_FILE = os.path.join(CWD, 'trending_keywords.txt')

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

        self.scraper_running = None 
        self.trending_keywords = list()
        self.current_keyword_index = None
        self.is_splash_running = None 

        self.load_trending_keywords()

        self.spider_names = ['cnn_spider', 'market_watch_spider', 'reuters_spider']
        # self.spider_names = ['cnn_spider']
        self.tasks_done = None

        self.scraping_hours = self._get_scraping_hours()
        self.is_scrapping = False

        self.main_frame.after(1000, self._loop)
    
    def load_trending_keywords(self):
        with open(self.TRENDING_KEYWORDS_FILE, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if line == '':
                    continue
                else:
                    now = datetime.now()
                    self.trending_keywords.append({'keyword': line, 'count': 0, 'date': now})
        
        self.control_panel.update_trending_keywords(self.trending_keywords)

    def show_controll_panel(self):
        print('shoing control panel')
        self.control_panel = ControllPanel(self.main_frame, self)
        self._show_widget(self.control_panel)
        self.control_panel.test_callback()
    
    def show_another_panel(self):
        print("showing another panel")
        w = AnotherPanel(self.main_frame)
        self._show_widget(w)
    
    def _show_widget(self, widget):
        widget.grid(row = 0, column = 0, sticky = 'nsew')
        widget.tkraise()
    
    def _add_log_to_controll_panel(self, text):
        self.control_panel.add_log(text)
    
    def task_done(self, result):
        self.tasks_done.append(result)
        self._add_log_to_controll_panel(f'[ DONE ] {str(result)}')

        if self.check_all_tasks_done():
            self._add_log_to_controll_panel('All tasks done')
    
    def check_all_tasks_done(self):
        # Simple logic, if tasks done list has equal number of elements with spider_names then it's true
        if len(self.tasks_done) == len(self.spider_names):
            return True
        else:
            return False

    def _start_scraper_async(self, keyword):

        #CAUTION: self.tasks_done must be init to be a list(), not gonna handle error here

        #Clear tasks done

        self.tasks_done.clear()

        data = self.news_collector.get_spider_data(keyword, 'business', False, 'today', 1)
        pool = Pool()
    
        # init pool
        for spider_name in self.spider_names:
            self._add_log_to_controll_panel(f'[ CNN Spider ],args: {str(data)}')
            pool.apply_async(self.news_collector.start_search_process, (data, spider_name), callback=self.task_done)
        # self._add_log_to_controll_panel(f'[ MarketWatcher spider ],args: {str(data)}')
        # pool.apply_async(self.news_collector.start_search_process, (data, 'market_watch_spider'), callback=self.task_done)
        # self._add_log_to_controll_panel(f'[ Reuters Spider ],args: {str(data)}')
        # pool.apply_async(self.news_collector.start_search_process, (data, 'reuters_spider'), callback=self.task_done)
        
        pool.close()
        print("end scraper")

    def _get_splash_container(self):
        return self.splash_container
    
    def _get_collector(self):
        return self.news_collector

    def start_splash(self):
        if self.splash_container.is_running() == False:
            self.control_panel.add_log("Splash container started by user")
            self.splash_container.start()
        else:
            self.control_panel.add_log("Splash container started by user but it's already running")

    def stop_splash(self):
        if self.splash_container.is_running() == True:
            print("Stopping splash ...")
            self.control_panel.add_log("Splash container stopped by user")
            # Using subprocess because Docker SDK has the following issue:
            # stop command sent but docker container not stopped,
            # it doesn't show up in 'docker ps' but you can 
            # 'docker logs -f splash' and see it's running  
            # self.splash_container.stop()
            # this is a temporary solution
            subprocess.run('docker rm -f splash'.split(" "))
    
    def _loop(self):
        is_running = self.splash_container.is_running()

        if is_running != self.is_splash_running:
            self.is_splash_running = is_running
            self.control_panel.toggle_docker_status(self.is_splash_running)
        
        #Prevent errors by skipping loop if docker splash container is not running
        if self.is_splash_running == False:
            self._add_log_to_controll_panel("Docker is not running, all scraping process will be hold")
            self.main_frame.after(1000, self._loop)
            return

        
        # scraping hours:
        # 6 A.M
        # 8 A.M
        # 10 A.M
        # 12 A.M
        # 2 P.M
        # 4 P.M
        # 6 P.M
        # 8 P.M
        # 10 P.M
        now = datetime.now()

        current_hour = now.hour

        if current_hour in self.scraping_hours:
            self.is_scrapping = True
        
        if self.is_scrapping == True:
            #Initiate scraping process if is_scraping = True
            if self.tasks_done == None:
                print("Starting from index 0")
                self.current_keyword_index = 0
                keyword = self.trending_keywords[self.current_keyword_index]['keyword']
                self.tasks_done = list()
                self._start_scraper_async(keyword)
                self.control_panel.update_scraping_keywords_index(self.current_keyword_index)
                self._add_log_to_controll_panel(f"Scraping with keyword: {keyword}")
            else:
                if self.check_all_tasks_done() == True:
                    if self.current_keyword_index < len(self.trending_keywords) - 1:
                        self.current_keyword_index += 1
                        keyword = self.trending_keywords[self.current_keyword_index]['keyword']
                        self._start_scraper_async(keyword)
                        self.control_panel.update_scraping_keywords_index(self.current_keyword_index)
                        self._add_log_to_controll_panel(f"Scraping with keyword: {keyword}")
                    else:
                        self.tasks_done = None 
                        self._add_log_to_controll_panel("Completely scraped all trending keywords")
                        self.is_scrapping = False

        self.main_frame.after(1000, self._loop)
    
    def start_scraping_trending_keywords(self):
        self.is_scrapping = True
    
    def _get_scraping_hours(self):
        return [7,10,13,16,18,21]

if __name__ == '__main__':
    root = MyApp()
    root.title('My app')
    root.mainloop()
