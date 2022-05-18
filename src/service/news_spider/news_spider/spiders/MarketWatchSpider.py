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
    name = 'market_watch_spider'
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
        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'{self.search_term}_{self.sections}_{(self.start_date.strftime("%m_%d_%Y_%H_%M_%S"))}')
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
        logging.basicConfig(level = logging.ERROR, handlers = [logging.FileHandler(self.LOG_FILE, mode= 'w'), stream_handler])
    
    def start_requests(self):
        query = 'apple'
        tab = 'Articles'
        page = 1
        url = 'https://www.marketwatch.com/search?q=apple&ts=0&tab=Articles'

        yield SplashRequest(url, callback = self.parse, args = {'wait': 5})
    
    def parse(self, response):
        print("parsing response")
        html_file = f"{response.url.split('/')[-1]}.html"

        html_saved_path = os.path.join(self.HTML_LOG_DIR,  html_file)
        with open(html_saved_path, 'wb') as file:
            logging.info(f"Saved html to {html_saved_path}")
            file.write(response.body)
    
        links = self._process_html_from_path(html_saved_path)

        for link in links:
            try:
                parsed_data = self._fetch_article(link)
                self._save_article(parsed_data)
            except Exception as e:
                print(str(e))
            finally:
                break

    def _process_html_from_path(self, html_path):
        '''
            parse html and return extracted links
            @params
                string html_path: path to html_file

            @return 
                [] valid_links: {'timestamp', 'link'}
        '''
        with open(html_path, 'r') as file:
            html = file.read()
        
        soup = bs(html)

        article_divs = soup.find_all('div', {'class':'element--article'})

        valid_links = list()
        for div in article_divs:
            h3 = div.find('h3', {'class': 'article__headline'})
            href = h3.find('a', {'class': 'link'}).attrs['href']
            if href == '#':
                break
            timestamp = int(div.attrs['data-timestamp'])//1000
            valid_links.append({'timestamp': timestamp, 'link': href})
            print(valid_links[-1])
        
        return valid_links
    
    def _fetch_article(self, link_data):
        '''
            Fetch article from link
            @params
                string link
            @return
                list of error links
        '''

        link = link_data['link']
        timestamp = link_data['timestamp']
        try:

            article = Article(link)

            article.download()
            article.parse()

            text = ''
            processed_text = ''

            for line in article.text.split("\n"):
                if line.startswith("Random reads") or line.startswith('Also read'):
                    break
                if line == 'text None':
                    break
                processed_text += line + '\n'
            article.text = processed_text

            text += f'link {link}\n'
            text += f'title {article.title}\n'
            text += f'text {article.text}\n'
            text += f'date {str(datetime.fromtimestamp(timestamp))}\n'
            text += f'authors {article.authors}\n'
            text += "#######\n"

            print(text)

            authors = list()
            for author in article.authors:
                authors.append(author)

            return {
                'url': link,
                'title': article.title,
                'text': article.text,
                'date': str(datetime.fromtimestamp(timestamp)),
                'authors': ','.join(authors),
            }

        except Exception as e:
            print(str(e))
            return link
        
    def _save_article(self, parsed_data):
        id = str(uuid.uuid4())
        extension = 'txt'
        meta_filename = f'{id}.{extension}'

        meta = list()
        # only allow digits and alphabet characters
        parsed_data['title'] = re.sub(r'[^a-zA-Z\s0-9]+', '', parsed_data['title'])

        meta.append('url,' + parsed_data['url'])
        meta.append('title,' + parsed_data['title'])
        meta.append('date,' + parsed_data['date'])
        meta.append('authors,' + parsed_data['authors'])

        print(meta)

        output_file = f"{id}_{parsed_data['title']}.{extension}"

        with open(os.path.join(self.META_DIR, meta_filename), 'w') as file:
            file.write('\n'.join(meta))
        
        with open(os.path.join(self.OUTPUT_DIR, output_file), 'w') as file:
            file.write(parsed_data['text'])




            


