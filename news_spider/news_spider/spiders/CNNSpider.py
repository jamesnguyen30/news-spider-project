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
from scrapy.utils.log import configure_logging
import time
import re

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()
CWD = os.path.join(CWD, 'output')

current_datetime = datetime.now()
LOG_DIR = os.path.join(CWD, 'log')
LOG_FILE = os.path.join(LOG_DIR, f'{str(current_datetime.date())}_{str(current_datetime.time())}.log')
HTML_LOG_DIR = os.path.join(LOG_DIR, 'html')
OUTPUT_DIR = os.path.join(CWD, 'dataset')
META_DIR = os.path.join(OUTPUT_DIR, 'metadata')
ERROR_LINKS_FILE = os.path.join(LOG_DIR, 'link_errors.log')

if os.path.exists(OUTPUT_DIR) == False:
    os.makedirs(OUTPUT_DIR)

if os.path.exists(META_DIR) == False:
    os.makedirs(META_DIR)

if os.path.exists(LOG_DIR) == False:
    os.makedirs(LOG_DIR)

if os.path.exists(HTML_LOG_DIR) == False:
    os.makedirs(HTML_LOG_DIR)

print(f"save data to {OUTPUT_DIR} and meta data to {META_DIR} and log to {LOG_FILE}")

logging.basicConfig(filename = LOG_FILE, level = logging.INFO)

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

    def __init__(self, *args, **kwargs):
        super(CNNSearchSpider, self).__init__(*args, **kwargs)
        configure_logging(install_root_handler=False)

    def start_requests(self):
        if self.retry == str(True):
            self._retry_error_links()
            return

        assert self.search_term != None, 'Search term is None'

        if self.sections == None:
            self.sections = 'business'

        for page in range(1,3):
            size = 50
            from_page = 50 * (page - 1)
            search_url = f'https://www.cnn.com/search?q={self.search_term}&size={size}&from={from_page}&page={page}&sections={self.sections}'
            print(search_url)
            yield SplashRequest(search_url, callback = self.parse, args = {'wait': 5})
    
    def parse(self, response):
        logging.info(f"Fetched {response.url}, extracting news results")
        html_file = f"{response.url.split('/')[-1]}.html"

        html_saved_path = os.path.join(HTML_LOG_DIR,  html_file)
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
            with open(os.path.join(OUTPUT_DIR, filename), 'w') as file:
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
            with open(os.path.join(META_DIR, meta_filename), 'w') as file:
                file.write('\n'.join(meta_content))
            
            logging.info(f"Saved to {OUTPUT_DIR} and metadata to {META_DIR}")
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

        with open(ERROR_LINKS_FILE, 'w') as file:
            logging.info(f"Saving {len(link_errors)} link errors to file: {ERROR_LINKS_FILE}")
            file.write('\n'.join(link_errors))
    
    def _retry_error_links(self):
        assert os.path.exists(ERROR_LINKS_FILE) == True, f"Attempting to retry error links but {ERROR_LINKS_FILE} is not found"

        logging.info(f'Loading error link file: {ERROR_LINKS_FILE}')

        with open(ERROR_LINKS_FILE, 'r') as file:
            links = file.readlines()
        error_links = list() 
        for link in links:
            error_links.append(self._fetch_article(link))
        
        with open(ERROR_LINKS_FILE, 'w') as file:
            logging.error(f'Found {len(error_links)}. Rewriting to {ERROR_LINKS_FILE}')
            file.write('\n'.join(error_links))
        
