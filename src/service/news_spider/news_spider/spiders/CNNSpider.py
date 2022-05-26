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
SERVICE_ROOT = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.append(str(SERVICE_ROOT))
print(SERVICE_ROOT)
print(sys.path)

from database import news_db

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

def check_and_create_dir(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

def get_date_format(date, date_only=False):
    if date_only:
        return f'{date.month}_{date.day}_{date.year}'
    return f'{date.month}_{date.day}_{date.year}_{date.hour}H_{date.minute}M'

class CnnSpider(scrapy.Spider):
    '''
        Depth-first CNN search spider
        specifically search for keyword
        @params:
            string search_term
            string sections 
            boolean retry = False (default)
            datetime start_date = datetime.now() (default), accept date format: 'm-d-yyyy' or quickly set 'today'
            int days_from_start_date = 1 (default)

        @returns
            list results
    '''
    name = 'cnn_spider'

    def __init__(self, search_term =None, sections = None, retry = False, start_date = None, days_from_start_date = None, *args, **kwargs, ):
        super(CnnSpider, self).__init__(*args, **kwargs)

        # Configure search params
        self.search_term = search_term
        self.sections = sections
        self.retry = retry
        self.start_date = start_date
        self.days_from_start_date = int(days_from_start_date)

        #Set up mongodb connection
        self.db = news_db.NewsDb()

        # Configure default date to scrape

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
        
        assert self.search_term != None, 'Search term is None'
        assert self.sections != None, 'Sections is None'

        #Initiate directories

        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'{self.search_term}_{self.sections}_{get_date_format(self.start_date)}_CNN')
        self.LOG_DIR = os.path.join(self.OUTPUT_DIR, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, f'_{self.search_term}_{self.sections}_{get_date_format(self.start_date)}_log.txt')
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
        if hasattr(self, 'retry'): 
            if self.retry == str(True):
                self._retry_error_links()
                return

        for page in range(1,3):
            size = 50
            from_page = 50 * (page - 1)
            search_url = f'https://www.cnn.com/search?q={self.search_term}&size={size}&from={from_page}&page={page}&sections={self.sections}'
            yield SplashRequest(search_url, callback = self.parse, args = {'wait': 5})
    
    def parse(self, response):
        logging.info(f"Fetched {response.url}, extracting news results")
        html_file = f"{response.url.split('/')[-1]}.html"

        html_saved_path = os.path.join(self.HTML_LOG_DIR,  html_file)
        with open(html_saved_path, 'wb') as file:
            logging.info(f"Saved html to {html_saved_path}")
            file.write(response.body)
    
        self._process_html_from_path(html_saved_path)
    
    def _fetch_article(self, link):
        '''
            Fetch article from link
            @params
                string link
            @return
                list of error links
        '''
        link_errors = list()

        try:
            logging.info(f"Extracting news at {link}")
            article = Article(link)
            article.download()
            article.parse()
            id = str(uuid.uuid4())
            extension = 'txt'

            # newspaper3k often parse with not all the article content. 
            # If there's a Read More text at the last line, trigger manual text parsing
            # This is an unknown error in newspaper3k
            
            last_line = article.text.split('\n')[-1]
            
            if last_line == 'Read More':
                text = self._manually_get_text(link)
                article.text = text

            #Filter out non-alphabet and non-digits character
            article.title = re.sub(r'[^a-zA-Z\s0-9]+', '', article.title)
            filename = f'{id}_{article.title}.{extension}'
            with open(os.path.join(self.OUTPUT_DIR, filename), 'w') as file:
                file.write(article.text)

            #Convert article publish date
            meta_content = list() 
            article.nlp()
            meta_content.append(f'url,{link}')
            meta_content.append(f'title,{article.title}')
            meta_content.append(f'authors,{article.authors}')
            meta_content.append(f'date, {article.publish_date}')
            meta_content.append(f'top_image,{article.top_image}')

            self._save_to_db(article.title, article.text, 'CNN',link, article.top_image, article.publish_date, article.authors)

            # if self.db.get_by_title(article.title) is not None:
            #     logging.warning(f"Skipping article '{article.title}' because it's already saved in database")
            #     return

            meta_filename = f'{id}.{extension}'
            with open(os.path.join(self.META_DIR, meta_filename), 'w') as file:
                file.write('\n'.join(meta_content))
            logging.info(f"Saved to {self.OUTPUT_DIR} and metadata to {self.META_DIR}")
        except Exception as e:
            logging.error(f'An error happend. check below')
            logging.error(str(e))
            link_errors.append(link)
        finally:
            return link_errors
        
    def _manually_get_text(self, link):

        html = requests.get(link)

        soup = BeautifulSoup(html.text)

        elements = soup.find_all(recursive=True, )

        text_element = list()
        for e in elements:
            try:
                for element_class in e.attrs['class']:
                    if element_class.startswith('zn-body__paragraph'):
                        text_element.append(e)
            except KeyError as error:
                continue
                    
        text = list()
        for e in text_element:
            text.append(e.text)

        print("Start from here:")
        return '\n'.join(text)

    def _process_html_from_path(self, path):

        with open(path, 'r') as file:
            html = file.read()
        
        soup = bs(html)
        result_contents = soup.find_all('div', {'class':'cnn-search__result-contents'})

        links = list()
        for div in result_contents:

            href = div.find("h3", {'class': 'cnn-search__result-headline'}).find('a').attrs['href']
            date = div.find('div', {'class': 'cnn-search__result-publish-date'}).find_all('span')[1].text
            date_obj = datetime.strptime(date, "%b %d, %Y")
            if date_obj < self.end_date:
                continue
            links.append('https:' + href)

        logging.info(f'found {len(links)} links before date: {self.end_date}')

        link_errors = list()
        for link in links:
            for error_link in self._fetch_article(link):
                link_errors.append(error_link)

        print(link_errors)
        with open(self.ERROR_LINKS_FILE, 'w') as file:
            logging.warning(f"Saving {len(link_errors)} link errors to file: {self.ERROR_LINKS_FILE}")
            if len(link_errors) > 0:
                for link in link_errors:
                    file.write(link)
            else:
                file.write("")


    def _retry_error_links(self):
        assert os.path.exists(self.ERROR_LINKS_FILE) == True, f"Attempting to retry error links but {self.ERROR_LINKS_FILE} is not found"

        logging.info(f'Loading error link file: {self.ERROR_LINKS_FILE}')

        with open(self.ERROR_LINKS_FILE, 'r') as file:
            links = file.readlines()
        error_links = list() 
        for link in links:
            error_links.append(self._fetch_article(link))
        
        with open(self.ERROR_LINKS_FILE, 'w') as file:
            logging.warning(f'Found {len(error_links)}. Rewriting to {self.ERROR_LINKS_FILE}')
            file.write('\n'.join(error_links))
        

    def _save_to_db(self, title:str, text:str, source:str = 'CNN', url:str = '', top_image_url:str = '', published_date:datetime = None, authors:str = None):
        news = self.db.get_by_title(title)
        #If the title doens't exist in database or this is a different search term
        print('published date ' , published_date)
        if news == None or news.search_term != self.search_term:
            if authors == None or len(authors) == 0:
                authors = ['na']
            try:
                self.db.save(self.search_term, title, text, authors, source, url, top_image_url, published_date)
            except Exception as e:
                logging.error("Failed to save to database, check below error")
                logging.error(e)
        else:
            logging.warning(f"Article with title: {title} exists in the database. Skip save")

        






