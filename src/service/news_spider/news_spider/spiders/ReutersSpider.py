# from scrapy_splash import SplashRequest
import scrapy
from scrapy import Request
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
from bs4 import BeautifulSoup
import sys
import pathlib
import json
import requests

SERVICE_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.append(str(SERVICE_ROOT))

from database import news_db

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

def check_and_create_dir(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

class ReutersSpider(scrapy.Spider):
    '''
        Depth-first Reuters search spider
        website: reuters.com

        @params:
            string search_term
            string sections
            boolean retry = False (default)
            datetime start_date = datetime.now() (default), accept date format: 'm-d-yyyy' or quickly set 'today'
            int days_from_start_date = 1 (default)

        @returns
            list results

        NOTE: add -s ROBOTTXT_OBEY=False to scrape this website
    '''
    name = 'reuters_spider'
    def __init__(self, search_term = None, sections = None, retry = False, start_date = None, days_from_start_date = 1 ,*args, **kwargs):
        super(ReutersSpider, self).__init__(*args, **kwargs)

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
        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'{self.search_term}_{self.sections}_{(self.start_date.strftime("%m_%d_%Y_%H_%M_%S"))}_REUTERS')
        self.LOG_DIR = os.path.join(self.OUTPUT_DIR, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, f'_{self.search_term}_{self.sections}_{self.start_date.strftime("%m_%d_%Y_%H_%M_%S")}_log.txt')
        self.JSON_LOG_DIR = os.path.join(self.LOG_DIR, 'json')
        self.META_DIR = os.path.join(self.OUTPUT_DIR, 'metadata')
        self.ERROR_LINKS_FILE = os.path.join(self.LOG_DIR, 'link_errors.log')

        check_and_create_dir(self.OUTPUT_DIR)
        check_and_create_dir(self.META_DIR)
        check_and_create_dir(self.LOG_DIR)
        check_and_create_dir(self.JSON_LOG_DIR)

        reload(logging)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        logging.basicConfig(level = logging.INFO, handlers = [logging.FileHandler(self.LOG_FILE, mode= 'w'), stream_handler])

        # Init db
        self.db = news_db.NewsDb()
    
    def start_requests(self):
        '''
        Reuters exposed its api for search so no need to use Splash request
        '''
        print("start request")
        # url = f'https://www.reuters.com/site-search/?query={self.search_term}&section={self.sections}&offset=0'
        url = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query={"keyword":"' + self.search_term + '","offset":10,"orderby":"display_date:desc","sections":"/' + self.sections+ '","size":10,"website":"reuters"}&d=95&_website=reuters'
        # yield Request(url, callback = self.parse)
        yield Request(url, callback=self.parse)
    
    def parse(self, response):
        # logging.info(f"Processing {response.url}")
        now = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

        json_file = f"{self.search_term}_{self.sections}_{now}.json"

        json_saved_path = os.path.join(self.JSON_LOG_DIR,  json_file)
        json_response = json.loads(response.body)

        print(json_response)

        with open(json_saved_path, 'w') as file:
            logging.info(f"Saved html to {json_saved_path}")
            json.dump(json_response, file)
