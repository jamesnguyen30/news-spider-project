from scrapy_splash import SplashRequest
import scrapy
from bs4 import BeautifulSoup as bs
import pathlib
import os
import nltk
import uuid
import logging
from datetime import datetime, timedelta
from newspaper import Article
import re
from imp import reload
import os
import requests
from bs4 import BeautifulSoup
import sys
import pathlib

SERVICE_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.append(str(SERVICE_ROOT))

from database import news_db

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

def check_and_create_dir(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

class MarketWatchSpider(scrapy.Spider):
    '''
        Depth-first Market watch search spider
        website: marketwatch.com

        @params:
            string search_term
            string sections
            boolean retry = False (default)
            datetime start_date = datetime.now() (default), accept date format: 'm-d-yyyy' or quickly set 'today'
            int days_from_start_date = 1 (default)

        @returns
            list results

        NOTE: add -s ROBOTTXT_OBEY=False to scrape this website
        sample: scrapy crawl market_watch_spider -a search_term=apple -a sections=business -a start-date=today -s ROBOTSTXT_OBEY=False
    '''
    name = 'reuters_spider'
    def __init__(self, search_term = None, sections = None, retry = False, start_date = None, days_from_start_date = 1 ,*args, **kwargs):
        super(MarketWatchSpider, self).__init__(*args, **kwargs)

        self.search_term = search_term
        self.sections = sections
        self.start_date = start_date
        self.days_from_start_date = int(days_from_start_date)

        if self.start_date == None or self.start_date.lower() == 'today':
            self.start_date = datetime.now()

        elif self.start_date == 'yesterday':
            self.start_date = datetime.now() - timedelta(days = 1)        

        else:
            self.start_date = datetime.strptime(self.start_date, '%m-%d-%Y')
        
        if self.days_from_start_date == None:
            self.days_from_start_date = 1
        
        self.end_date = self.start_date - timedelta(days = self.days_from_start_date)
        self.end_date = self.end_date.replace(hour = 0, minute = 0, second = 0)

        self.retry = retry
        # self.start_date = start_date
        # self.days_from_start_date = int(days_from_start_date)
        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'{self.search_term}_{self.sections}_{(self.start_date.strftime("%m_%d_%Y_%H_%M_%S"))}_MARTKETWATCH')
        self.LOG_DIR = os.path.join(self.OUTPUT_DIR, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, f'_{self.search_term}_{self.sections}_{self.start_date.strftime("%m_%d_%Y_%H_%M_%S")}_log.txt')
        self.HTML_LOG_DIR = os.path.join(self.LOG_DIR, 'html')
        self.META_DIR = os.path.join(self.OUTPUT_DIR, 'metadata')
        self.ERROR_LINKS_FILE = os.path.join(self.LOG_DIR, 'link_errors.log')

        check_and_create_dir(self.OUTPUT_DIR)
        check_and_create_dir(self.META_DIR)
        check_and_create_dir(self.LOG_DIR)
        check_and_create_dir(self.HTML_LOG_DIR)

        reload(logging)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        logging.basicConfig(level = logging.INFO, handlers = [logging.FileHandler(self.LOG_FILE, mode= 'w'), stream_handler])

        # Init db
        self.db = news_db.NewsDb()
    
    def start_requests(self):
        query = 'apple'
        tab = 'Articles'
        page = 1
        url = 'https://www.marketwatch.com/search?q=apple&ts=0&tab=Articles'

        yield SplashRequest(url, callback = self.parse, args = {'wait': 5})