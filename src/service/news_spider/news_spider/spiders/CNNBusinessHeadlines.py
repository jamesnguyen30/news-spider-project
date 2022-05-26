from scrapy_splash import SplashRequest
import scrapy
from bs4 import BeautifulSoup as bs
import pathlib
import os
import nltk
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
import pandas as pd
from collections import Counter

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

        self.OUTPUT_DIR = os.path.join(CWD, 'dataset', 'headlines', f"CNN_{now.month}_{now.day}_{now.year}")
        self.OUTPUT_FILE = os.path.join(self.OUTPUT_DIR, f'headlines.csv')

        check_and_create_dir(self.OUTPUT_DIR)

        try:
            print(f"{self.OUTPUT_FILE} loaded")
            self.df = pd.read_csv(self.OUTPUT_FILE)
        except Exception as e:
            print(f"{self.OUTPUT_FILE} doesn't exist, creating one ... ")
            self.df = pd.DataFrame([], columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url'])
            print(str(e))

        self.counter_url = Counter()

        # Add all scraped URLs to counter to prevent duplication
        for index, row in self.df.iterrows():
            if row['url'] not in self.counter_url:
                self.counter_url[row['url']]+=1
            
        print('counter url =', str(self.counter_url))
    
    def start_requests(self):
        print('Fetching business healdines')
        url = f'https://www.cnn.com/{self.sections}'
        yield SplashRequest(url, callback = self.parse, args = {'wait': 5})
    
    def parse(self, response):
        logging.info(f"{datetime.now()} Fetched {response.url}")
        html_path = os.path.join(self.OUTPUT_DIR, 'cnn_headlines.html')
        html = response.body

        with open(html_path, 'wb') as file:
            logging.info(f"Saved html to {html_path}")
            file.write(response.body)
        
        self._process_html(html)
    
    def _process_html(self, html):
        links = self._get_all_links(html)

        data_list = list()

        for link in links:
            try:
                if self._check_if_url_exists(link):
                    print("URL existed")
                    continue
                
                self.counter_url[link] += 1

                data = self._fetch_article(link)
                data_list.append([
                    data['title'],
                    data['date'],
                    data['text'],
                    data['authors'],
                    data['source'],
                    data['url'],
                    data['image_url']
                ])

            except Exception as e:
                print(str(e))
                continue
        
        new_df = pd.DataFrame(data_list, columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url'])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.df.to_csv(self.OUTPUT_FILE, index = False)
    
    def _check_if_url_exists(self, url):
        if url in self.counter_url:
            return True
        return False


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
            print(f"Extracting news at {link}")
            article = Article(link)
            article.download()
            article.parse()

            # newspaper3k often parse with not all the article content. 
            # If there's a Read More text at the last line, trigger manual text parsing
            # This is an unknown error in newspaper3k
            
            last_line = article.text.split('\n')[-1]
            
            if last_line == 'Read More':
                text = self._manually_get_text(link)
                article.text = text

            #Filter out non-alphabet and non-digits character
            article.title = re.sub(r'[^a-zA-Z\s0-9]+', '', article.title)

            return {
                'title': article.title,
                'date': article.publish_date,
                'text': article.text,
                'authors': article.authors,
                'source': 'CNN',
                'url': link,
                'image_url': article.top_image
            }

            # if self.db.get_by_title(article.title) is not None:
            #     logging.warning(f"Skipping article '{article.title}' because it's already saved in database")
            #     return
        except Exception as e:
            print(str(e))
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

    def _get_all_links(self, html):
        soup = bs(html)

        all_a_tags = soup.find_all('a')
        hrefs = list()
        for a in all_a_tags:
            try:
                href = a.attrs['href']
                if href.endswith(f'index.html'):
                    hrefs.append(f"https://www.cnn.com{href}")

            except Exception as e:
                print(str(e))
                continue
        
        return hrefs
        






