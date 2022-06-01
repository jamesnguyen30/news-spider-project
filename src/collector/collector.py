from bs4 import BeautifulSoup as bs
from multiprocessing import Pool
import subprocess
import os
import pathlib
import json 
from newsapi import NewsApiClient
import pathlib
import os
import requests
from newspaper import Article
import pandas as pd
from datetime import datetime
from nlp import entity_extractor
from utils import data

now = datetime.now()

ROOT = pathlib.Path(__file__).parent.parent.absolute()
CWD = pathlib.Path(__file__).parent.absolute()

NEWS_SPIDER_PATH = os.path.join(ROOT, 'service', 'news_spider', 'news_spider')
SECRET_DIR = os.path.join(ROOT, 'secrets', 'newsapi_key.txt')
OUTPUT_DIR = os.path.join(CWD, 'output') 
HEADLINE_CSV_PATH = os.path.join(OUTPUT_DIR, f'cnn_headlines_{now.month}_{now.day}_{now.year}.csv')

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
    print(f"created new output dir {OUTPUT_DIR}")

class NewsCollector():

    def __init__(self):
        self.entity_extractor = entity_extractor.EntityExtractor(OUTPUT_DIR)
        self.collected_data = data.CollectedData(HEADLINE_CSV_PATH)

    def _get_newsapi_headlines(self, save_csv):
        '''
            get the current business headlines with news api
            @params:
                boolean save_csv: set True to save headlines to CSV
            @return
                list headlines
        '''
        try:
            with open(SECRET_DIR, 'r') as file:
                apikey = file.readline()
        
        except Exception as e:
            print(str(e))
            print(f"the file newsapi_key.txt is not found. Make sure to put the key in side that file in dir: {SECRET_DIR}")
            print("operation canceled")
            return

        newsapi = NewsApiClient(api_key = apikey)

        headlines = newsapi.get_top_headlines(q='', category='business')

        if headlines['status'] != 'ok':
            print("Error while calling NewsApi")
            return
        
        print(f"NEWS API STATUS: {headlines['status']}")
        error_links = list()

        for headline in headlines['articles']:
            try:

                article = Article(headline['url'])
                if headline['source']['name'] == 'YouTube':
                    # Note: ignore this source because its text is empty 
                    continue

                if headline['source']['name'] == 'CNBC':
                    headline['content'] = self.cnbc_parser(headline['url'])

                else:
                    article.download()
                    article.parse()
                    headline['content'] = article.text

                print(f"Extracted content for {headline['title']}")
                self.collected_data.add_data(
                    title = headline['title'], 
                    date = headline['publishedAt'],
                    text = headline['content'],
                    authors = headline['author'],
                    source = headline['source']['name'], 
                    url = headline['url'], 
                    image_url = headline['urlToImage'],
                    search_term = 'headlines'
                )

            except Exception as e:
                print(f" error link: {headline['url']}\n{str(e)}")
                error_links.append(headline['url'])
            
        print('Error links : ' + str(error_links))

        if save_csv:
            self.collected_data.to_csv(HEADLINE_CSV_PATH)
        
        return headlines 
    
    def get_trending_stock(self):
        '''
        used stockanalysis.com API : https://stockanalysis.com/trending/
        @return
            dict json_response: response has the following format:
            {
                'status': number,
                'data': [
                    {
                        's': symbol
                        'n': company name,
                        'views': number
                        'rank': null,
                        'marketCap': number,
                        'change': float,
                        'volume': number
                        'price': float
                    },
                    ....
                ]
            }
        '''

        url = 'https://api.stockanalysis.com/wp-json/sa/select?index=stocks&main=views&count=20&sort=desc&columns=rank,s,n,views,marketCap,change,volume,price&filters='
        headers = {
            'accept': '*/*',
            'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
        }
        response = requests.get(url, headers = headers)
        json_response = json.loads(response.content.decode('utf-8'))
        
        return json_response["data"]
    
    def get_trending_keywords(self, debug=False):
        # collector = NewsCollector()
        counter = collector.entity_extractor.process_data(HEADLINE_CSV_PATH, True)
        collector.entity_extractor.save_counter()
        if debug:
            print("Trending keywords:")
            print(counter)
            print(f"Trending keywords saved to {OUTPUT_DIR}")

    def cnbc_parser(self, link):
        '''
        parser specifically for CNBC news
        updated: 5.25.2022

        @params:
            string link: link to article
        
        @return:
            string text: parsed text
        '''
        response = requests.get(link)

        html = response.text

        soup = bs(html)

        # regex = re.compile('^PageBuilder-article')
        ArticleBody = soup.find('div', {'class': 'ArticleBody-articleBody'})

        divs = ArticleBody.find_all('div', {'class': "group"})
        text = list()

        for div in divs:

            elements = div.find_all(recursive=True)

            for e in elements:
                if e.name == 'a' or e.text.startswith('Subscribe to CNBC on YouTube.'):
                    continue
                
                if 'Sign up now' in e.text:
                    break

                text.append(e.text)

        return '\n'.join(text)
        
    def get_cnn_headlines(self):
        print("Getting CNN Headlines")
        print(f"PID={os.getpid()}")

        proc = subprocess.Popen(f'''scrapy crawl cnn_business_headlines_spider -a output_dir={OUTPUT_DIR} -a sections=business -s ROBOTSTXT_OBEY=False'''.split(" "),
            cwd=NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        print("Waiting for subprocess to complete") 
        proc.wait()
        print(f"Subprocess is done with code {proc.returncode}")
        return {'spider': 'CNN Headline Spider', 'return_code': proc.returncode, 'pid': os.getpid()}

    def start_cnn_search(self, data):
        print('CNN Spider process PID=', os.getpid())
        proc = subprocess.Popen(f'''scrapy crawl cnn_search_spider -a search_term="{data['search_term']}" -a sections={data['sections']} -a retry={data['retry']} -a start_date={data['start_date']} -a days_from_start_date={data['days_from_start_date']} -s LOG_ENABLED=False'''.split(" "),\
                cwd=NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        proc.wait()
        proc.poll()
        return {'spider': 'CNN Spider', 'return_code': proc.returncode, 'params': data, 'pid': os.getpid()}

    def start_search_process(self, data, spider_name):
        print('Spider process PID=', os.getpid())
        command = f"scrapy crawl {spider_name} -a search_term={data['search_term']} -a sections={data['sections']} -a retry={data['retry']} -a start_date={data['start_date']} -a days_from_start_date={data['days_from_start_date']} -s LOG_ENABLED=False -s ROBOTSTXT_OBEY=False".split(" ")
        print('command ' + str(command))
        proc = subprocess.Popen(command, cwd=NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        proc.wait()
        proc.poll()
        return {'spider': spider_name, 'return_code': proc.returncode, 'params': data, 'pid': os.getpid()}

    def get_cnn_spider_data(self, search_term:str, sections:str, retry:bool = False, start_date: str = 'today', days_from_start_date: int = 1):
        return {
            'search_term': search_term,
            'sections': sections,
            'retry': retry,
            'start_date': start_date,
            'days_from_start_date': days_from_start_date
            }
        
    def get_spider_data(self, search_term:str, sections:str, retry:bool = False, start_date: str = 'today', days_from_start_date: int = 1):
        return {
            'search_term': search_term,
            'sections': sections,
            'retry': retry,
            'start_date': start_date,
            'days_from_start_date': days_from_start_date
            }
        
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

if __name__ == '__main__':
    collector = NewsCollector()
    now = datetime.now()
    # collector._start_get_cnn_headlines()
    # headlines = collector._get_newsapi_headlines(True)

    collector.get_cnn_headlines()

    # counter = collector.entity_extractor.process_data(HEADLINE_CSV_PATH, True)
    # collector.entity_extractor.save_counter()
    # print(counter)