from multiprocessing import Pool
import subprocess
import os
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.absolute()

NEWS_SPIDER_PATH = os.path.join(ROOT, 'service', 'news_spider', 'news_spider')

class NewsCollector():

    def __init__(self):
        pass

    def start_cnn_search(self, data):
        print('CNN Spider process PID=', os.getpid())
        proc = subprocess.Popen(f"scrapy crawl cnn_search_spider -a search_term={data['search_term']} -a sections={data['sections']} -a retry={data['retry']} -a start_date={data['start_date']} -a days_from_start_date={data['days_from_start_date']} -s LOG_ENABLED=False".split(" "),\
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
    # def get_reuters_spider_data(self, search_term:str, sections:str, retry:bool = False, start_date: str = 'today', days_from_start_date: int = 1):
    #     return {
    #         'search_term': search_term,
    #         'sections': sections,
    #         'retry': retry,
    #         'start_date': start_date,
    #         'days_from_start_date': days_from_start_date
    #         }
