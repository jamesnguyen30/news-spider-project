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

ROOT = pathlib.Path(__file__).parent.parent.absolute()
CWD = pathlib.Path(__file__).parent.absolute()

NEWS_SPIDER_PATH = os.path.join(ROOT, 'service', 'news_spider', 'news_spider')
SECRET_DIR = os.path.join(ROOT, 'secrets', 'newsapi_key.txt')
OUTPUT_DIR = os.path.join(CWD, 'output') 

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
    print(f"created new output dir {OUTPUT_DIR}")

class NewsCollector():

    def __init__(self):
        pass

    def _get_current_headlines(self, save_csv = True):
        '''
            get the current business headlines with news api
            @params:
                string output: path to output file. 
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

        # with open('newsapi_result.json', 'w') as file:
        #     json.dump(headlines, file)

        # Process response from newsapi top headlines

        # with open('newsapi_result.json', 'r') as file:
        #     headlines = json.load(file)

        if headlines['status'] != 'ok':
            print("Error while calling NewsApi")
            print(print(headlines))
            return

        print(f"NEWS API STATUS: {headlines['status']}")
        error_links = list()
        data = list()

        for headline in headlines['articles']:
            try:
                article = Article(headline['url'])

                if headline['source']['name'] == 'CNBC':
                    headline['content'] = self.cnbc_parser(headline['url'])

                else:
                    article.download()
                    article.parse()
                    headline['content'] = article.text

                print(f"Extracted content for {headline['title']}")
                data.append([
                    headline['title'], 
                    headline['publishedAt'],
                    headline['content'],
                    headline['author'],
                    headline['source']['name'], 
                    headline['url'], 
                    headline['urlToImage']
                ])
            except Exception as e:
                print(f" error link: {headline['url']}\n{str(e)}")
                error_links.append(headline['url'])
            
        print('Error links : ' + str(error_links))

        if save_csv:
            now = datetime.now()
            df = pd.DataFrame(data, columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url'])
            df.to_csv(os.path.join(OUTPUT_DIR, f'headlines_{now.month}_{now.day}_{now.year}_{now.hour}_{now.minute}.csv'))
        
        return data

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

if __name__ == '__main__':
    collector = NewsCollector()
    headlines = collector._get_current_headlines()

    print(headlines)