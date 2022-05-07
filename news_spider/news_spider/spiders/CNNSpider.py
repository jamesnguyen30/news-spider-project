from gettext import install
import scrapy
from scrapy_splash import SplashRequest
from scrapy import cmdline
from bs4 import BeautifulSoup as bs
import pathlib
import os
import nltk
import uuid
import logging
from datetime import datetime
from newspaper import Article
import re
from imp import reload

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

def check_and_create_dir(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

def get_date_format(date):
    return f'{date.month}_{date.day}_{date.year}_{date.hour}H_{date.minute}M'

class CNNSearchSpider(scrapy.Spider):
    '''
        Depth-first CNN search spider
        specifically search for keyword
        @params:
            string search_term
        @returns
            list results
    '''
    name = 'cnn_search_spider'

    def __init__(self, search_term =None, sections = None, retry = False, *args, **kwargs, ):
        super(CNNSearchSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term
        self.sections = sections
        
        assert self.search_term != None, 'Search term is None'
        assert self.sections != None, 'Sections is  is None'

        #Initiate directories

        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', f'{self.search_term}_{self.sections}_{get_date_format(datetime.now())}')
        self.LOG_DIR = os.path.join(self.OUTPUT_DIR, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, f'_{self.search_term}_{self.sections}_{get_date_format(datetime.now())}_log.txt')
        self.HTML_LOG_DIR = os.path.join(self.LOG_DIR, 'html')
        self.META_DIR = os.path.join(self.OUTPUT_DIR, 'metadata')
        self.ERROR_LINKS_FILE = os.path.join(self.LOG_DIR, 'link_errors.log')
        
        check_and_create_dir(self.OUTPUT_DIR)
        check_and_create_dir(self.META_DIR)
        check_and_create_dir(self.LOG_DIR)
        check_and_create_dir(self.HTML_LOG_DIR)

        print(f"save data to {self.OUTPUT_DIR} and meta data to {self.META_DIR} and log to {self.LOG_FILE}")
        reload(logging)
        logging.basicConfig(filename = self.LOG_FILE, level = logging.INFO)
        print("Saving log to ", self.LOG_FILE)

    def start_requests(self):
        if hasattr(self, 'retry'): 
            if self.retry == str(True):
                self._retry_error_links()
                return

        for page in range(1,3):
            size = 50
            from_page = 50 * (page - 1)
            search_url = f'https://www.cnn.com/search?q={self.search_term}&size={size}&from={from_page}&page={page}&sections={self.sections}'
            print(search_url)
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

            #Filter out non-alphabet and non-digits character
            article.title = re.sub(r'[^a-zA-Z\s0-9]+', '', article.title)
            filename = f'{id}_{article.title}.{extension}'
            with open(os.path.join(self.OUTPUT_DIR, filename), 'w') as file:
                file.write(article.text)
            print(f'body: {article.text}')

            meta_content = list() 
            article.nlp()
            meta_content.append(f'url:{link}')
            meta_content.append(f'summary:{article.summary}')
            meta_content.append(f'keywords:{article.keywords}')
            meta_content.append(f'top image:{article.top_image}')
            meta_content.append(f'authors:{article.authors}')
            meta_content.append(f'date:{article.publish_date}')
            meta_content.append(f'title:{article.title}')

            print('\n'.join(meta_content))

            meta_filename = f'{id}.{extension}'
            with open(os.path.join(self.META_DIR, meta_filename), 'w') as file:
                file.write('\n'.join(meta_content))
            
            logging.info(f"Saved to {self.OUTPUT_DIR} and metadata to {self.META_DIR}")
        except Exception as e:
            logging.error(f'An error happend at link: {link}. Saving to error-links.log')
            link_errors.append(link)
            logging.error(e)
        finally:
            return link_errors

    def _process_html_from_path(self, path):

        with open(path, 'r') as file:
            html = file.read()
        
        soup = bs(html)

        h3_headlines = soup.find_all('h3', {'class': 'cnn-search__result-headline'})

        links = list()

        for h3 in h3_headlines:
            href = h3.find("a").attrs['href']
            links.append("https:" + href)

        logging.info(f'found {len(links)} links')

        link_errors = list()
        for link in links:
            link_errors.append(self._fetch_article(link))
            break

        with open(self.ERROR_LINKS_FILE, 'w') as file:
            logging.info(f"Saving {len(link_errors)} link errors to file: {self.ERROR_LINKS_FILE}")
            to_write = '\n'.join(link_errors)
            if len(link_errors) > 0:
                file.write(to_write)
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
            logging.error(f'Found {len(error_links)}. Rewriting to {self.ERROR_LINKS_FILE}')
            file.write('\n'.join(error_links))
        
