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

#append path to search for database service
# SERVICE_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
# sys.path.append(str(SERVICE_ROOT))

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

def check_and_create_dir(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

class CNNBusinessHeadlines(scrapy.Spider):
    '''
        Scrape CNN business headlines every day
        Save data to csv
        @params:
            string sections 
            boolean retry = False (default)
        @returns
            list results
    '''

    name = 'cnn_business_headlines_spider'

    def __init__(self, sections = None, retry = False, *args, **kwargs, ):
        super(CNNBusinessHeadlines, self).__init__(*args, **kwargs)

        self.sections = sections
        assert self.sections!= None, 'Section cannot be None'

        now = datetime.now()

        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'CNN_{self.sections}_headlines_{now.month}_{now.day}_{now.year}_{now.hour}_{now.minute}')
        self.LOG_DIR = os.path.join(self.OUTPUT_DIR, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, f'CNN_{self.sections}_headlines_{now.month}_{now.day}_{now.year}_{now.hour}_{now.minute}_log.txt')

        check_and_create_dir(self.OUTPUT_DIR)
        check_and_create_dir(self.LOG_DIR)

        reload(logging)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        logging.basicConfig(level = logging.ERROR, handlers = [logging.FileHandler(self.LOG_FILE, mode= 'w'), stream_handler])
    
    def start_requests(self):
        url = 'https://www.cnn.com/business'
        yield SplashRequest(url, callback = self.parse, args = {'wait': 5})
    
    def parse(self, response):
        logging.info(f"{datetime.now()} Fetched {response.url}")
        print(response)
        html_path = os.path.join(self.OUTPUT_DIR, 'cnn_headlines.html')

        with open(html_path, 'wb') as file:
            logging.info(f"Saved html to {html_path}")
            file.write(response.body)
        






