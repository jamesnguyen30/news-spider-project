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

        # number of returned articles
        SIZE = 20
        print("start request")
        url = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query={"keyword":"' + self.search_term + '","offset":0,"orderby":"display_date:desc","sections":"/' + self.sections+ '","size":' + str(SIZE) +',"website":"reuters"}&d=95&_website=reuters'
        yield Request(url, callback=self.parse)

    def _fetch_article(self, article):
        authors = list()
        for author in article['authors']:
            authors.append(author['name'])

        data = {
            'url': f"https://www.reuters.com{article['canonical_url']}",
            'title': article['title'],
            'authors': authors
        }

        dateobj = datetime.strptime(article['display_time'], "%Y-%m-%dT%H:%M:%S%z")
        dateobj = dateobj.replace(tzinfo = None)

        #Only fetch article before end date
        if dateobj < self.end_date:
            return None

        news_article = Article(data['url'])
        news_article.download()
        news_article.parse()

        text = list()

        for line in news_article.text.split("\n"):
            #  ignore these lines because they are paywall
            if (line.startswith('Register now for FREE')) or (line.startswith('Reporting by')) or (line.startswith('Our Standards:')):
                continue
            else:
                text.append(line)

        # Remove the first line of each article because most of them is small description for 
        # illustration image

        data['text'] = '\n'.join(text[1:])
        data['top_image'] = news_article.top_image
        data['date'] = dateobj

        return data
    
    def parse(self, response):
        now = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

        json_file = f"{self.search_term}_{self.sections}_{now}.json"

        json_saved_path = os.path.join(self.JSON_LOG_DIR,  json_file)
        parsed = json.loads(response.body)

        print('status code ' + str(parsed['statusCode']))
        articles = parsed['result']['articles']
        print(f'articles count {len(articles)}')
        try:
            for article in articles:
                parsed_data = self._fetch_article(article)
                if parsed_data == None:
                    break
                self._save_article(parsed_data)
        except Exception as e:
            logging.error("Error while fetching article with newspaper3k, check error below")
            logging.error(str(e))

        with open(json_saved_path, 'w') as file:
            logging.info(f"Saved html to {json_saved_path}")
            json.dump(parsed, file)

    def _save_article(self, parsed_data):
        '''
        parsed data structure must meet these requirements:
        string title
        string url
        array authors
        datetime date
        string top_image
        string text // article body text
        '''

        id = str(uuid.uuid4())
        extension = 'txt'
        meta_filename = f'{id}.{extension}'

        meta = list()
        # only allow digits and alphabet characters
        parsed_data['title'] = re.sub(r'[^a-zA-Z\s0-9]+', '', parsed_data['title'])

        meta.append('url,' + parsed_data['url'])
        meta.append('title,' + parsed_data['title'])
        meta.append('authors,' + '.'.join(parsed_data['authors']))
        meta.append('date,' + str(parsed_data['date']))
        meta.append('top_image,' + parsed_data['top_image'])

        output_file = f"{id}_{parsed_data['title']}.{extension}"

        try:
            with open(os.path.join(self.META_DIR, meta_filename), 'w') as file:
                file.write('\n'.join(meta))
            logging.info(f"Saved meta file {meta_filename}")
        except Exception as e:
            logging.error(f"Error while saving {meta_filename}")

        try: 
            with open(os.path.join(self.OUTPUT_DIR, output_file), 'w') as file:
                file.write(parsed_data['text'])
            logging.info(f"Saved to output file {output_file}")
        except Exception as e:
            logging.error(f"Error while saving {output_file}")
            logging.error(str(e))

        # save to database

        # try:
        #     self._save_to_db(parsed_data['title'], parsed_data['text'], 'MartketWatch',\
        #          parsed_data['url'], parsed_data['top_image'], parsed_data['date'], parsed_data['authors'])
        # except Exception as e:
        #     logging.error("Error while saving to db")
        #     logging.error(str(e))
