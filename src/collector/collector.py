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
from multiprocessing import Process, Pool
import sys
import traceback
from collections import Counter

now = datetime.now()

ROOT = pathlib.Path(__file__).parent.parent.absolute()
CWD = pathlib.Path(__file__).parent.absolute()

sys.path.append(str(CWD))
from nlp import entity_extractor, summarizer, collected_data 

class NewsCollector():
    '''
        Collect headlines and run search on CNN, Reuters, MarketWatch using keywords
    '''
    def __init__(self):

        now = datetime.now()

        self.NEWS_SPIDER_PATH = os.path.join(
            ROOT, 'service', 'news_spider', 'news_spider')
        self.SECRET_DIR = os.path.join(ROOT, 'secrets', 'newsapi_key.txt')
        self.OUTPUT_DIR = os.path.join(CWD, 'output')

        self.HEADLINE_CSV_PATH = os.path.join(
            self.OUTPUT_DIR, f'headlines_{now.month}_{now.day}_{now.year}.csv')
        self.SPIDER_NAMES = ['cnn_spider',
                             'market_watch_spider', 'reuters_spider']

        if os.path.exists(self.OUTPUT_DIR) == False:
            os.mkdir(self.OUTPUT_DIR)
            print(f"created new output dir {self.OUTPUT_DIR}")

        self.entity_extractor = entity_extractor.EntityExtractor(self.OUTPUT_DIR)
        self.trending_keyword_filename = self.entity_extractor.TRENDING_KEYWORDS_FILE
        self.collected_data = collected_data.CollectedData(self.HEADLINE_CSV_PATH)
        self.summarizer = summarizer.SimpleSummarizer()

    def _get_newsapi_headlines(self, save_csv):
        '''
            get the current business headlines with news api
            @params:
                boolean save_csv: set True to save headlines to CSV
            @return
                list headlines
        '''
        try:
            with open(self.SECRET_DIR, 'r') as file:
                apikey = file.readline()

        except Exception as e:
            print(str(e))
            print(
                f"the file newsapi_key.txt is not found. Make sure to put the key in side that file in dir: {self.SECRET_DIR}")
            print("operation canceled")
            return

        newsapi = NewsApiClient(api_key=apikey)

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

                # counter = self.entity_extractor.count_entities(headline['content'])

                # keywords = list()

                # for key, value in counter.most_common():
                #     keywords.append(key)

                # summary = self.summarizer.summarize(headline['content'])

                self.collected_data.add_data(
                    title=headline['title'],
                    date=headline['publishedAt'],
                    text=headline['content'],
                    authors=headline['author'],
                    source=headline['source']['name'],
                    url=headline['url'],
                    image_url=headline['urlToImage'],
                    search_term='headlines',
                )

            except Exception as e:
                print(f" error link: {headline['url']}\n{str(e)}")
                error_links.append(headline['url'])
                traceback.print_exc()

        print('Error links : ' + str(error_links))

        if save_csv:
            self.collected_data.to_csv(self.HEADLINE_CSV_PATH, True)

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
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        json_response = json.loads(response.content.decode('utf-8'))

        return json_response["data"]

    def get_trending_keywords(self, debug=False):
        # collector = NewsCollector()
        counter = self.entity_extractor.get_trending_keywords(
            self.HEADLINE_CSV_PATH, True)
        self.entity_extractor.save_trending_keywords()
        if debug:
            print("Trending keywords:")
            print(counter)
            print(f"Trending keywords saved to {self.OUTPUT_DIR}")

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

    def start_get_cnn_headlines(self, detach = True):
        p = Process(target=self._get_cnn_headlines)
        p.start()
        if detach == False:
            p.join()

    def fetch_news_based_on_keywords(self):
        print("Fetching news based on trending keywords ...")
        print(f"PID={os.getpid()}")

        try:
            keywords = list()
            with open(self.trending_keyword_filename, 'r') as file:
                for line in file.readlines():
                    key, value = line.split(":")

                    keywords.append(key)

            for keyword in keywords:
                pool = Pool()
                data = self.get_spider_data(
                    keyword, 'business', False, 'today', 1)

                for spider in self.SPIDER_NAMES:
                    pool.apply_async(self.start_search_process, (data, spider),
                                     callback=lambda: print(f"{spider} is done"))

                pool.close()

        except Exception as e:
            print(str(e))

    def _get_cnn_headlines(self):
        print("Getting CNN Headlines")
        print(f"PID={os.getpid()}")

        proc = subprocess.Popen(f'''scrapy crawl cnn_business_headlines_spider -a output_dir={self.OUTPUT_DIR} -a sections=business -s ROBOTSTXT_OBEY=False'''.split(" "),
                                cwd=self.NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        print("Waiting for subprocess to complete")
        proc.wait()
        print(f"Subprocess is done with code {proc.returncode}")
        return {'spider': 'CNN Headline Spider', 'return_code': proc.returncode, 'pid': os.getpid()}

    def start_search_process(self, data, spider_name):
        print(data)
        print('Spider process PID=', os.getpid())
        # command = f'''scrapy crawl {spider_name} -a search_term="{data['search_term']}" -a sections={data['sections']} -a retry={data['retry']} -a start_date={data['start_date']} -a days_from_start_date={data['days_from_start_date']} -s LOG_ENABLED=False -s ROBOTSTXT_OBEY=False'''.split(" ")
        command = [
            'scrapy', 
            'crawl', 
            spider_name, 
            '-a', f'''search_term="{data['search_term']}"''',
            '-a', f'''sections={data['sections']}''',
            '-a', f'''retry={data['retry']}''',
            '-a', f'''start_date={data['start_date']}''',
            '-a', f'''days_from_start_date={data['days_from_start_date']}''',
            '-s', 'LOG_ENABLED=False',
            '-s', 'ROBOTSTXT_OBEY=False',
            ]
        print('command ' + str(command))
        proc = subprocess.Popen(
            command, cwd=self.NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        proc.wait()
        proc.poll()
        return {'spider': spider_name, 'return_code': proc.returncode, 'params': data, 'pid': os.getpid()}

    def get_spider_data(self, search_term: str, sections: str, retry: bool = False, start_date: str = 'today', days_from_start_date: int = 1):
        return {
            'search_term': search_term,
            'sections': sections,
            'retry': retry,
            'start_date': start_date,
            'days_from_start_date': days_from_start_date
        }
    
    def generate_trending_keywords_from_today_headlines(self):
        self.entity_extractor.generate_trending_keywords(self.HEADLINE_CSV_PATH, True)
        self.entity_extractor.save_trending_keywords()
    
    def get_trending_keywords(self):
        return self.entity_extractor.trending_keywords
