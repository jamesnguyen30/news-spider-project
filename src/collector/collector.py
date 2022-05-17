from multiprocessing import Pool
import subprocess
import os
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.absolute()

NEWS_SPIDER_PATH = os.path.join(ROOT, 'service', 'news_spider', 'news_spider')

class NewsCollector():

    def __init__(self):
        pass

    def start_cnn_search(self, data, proc_dict = None):
        print('Started new process pid=', os.getpid())
        if proc_dict != None:
            proc_dict[os.getpid()] = True
        proc = subprocess.Popen(f"scrapy crawl cnn_search_spider -a search_term={data['search_term']} -a sections={data['sections']} -a retry={data['retry']} -a start_date={data['start_date']} -a days_from_start_date={data['days_from_start_date']} -s LOG_ENABLED=False".split(" "),\
                cwd=NEWS_SPIDER_PATH, stdout=subprocess.PIPE, encoding='utf-8')
        proc.wait()
        proc.poll()
        print('completed with return code ', proc.returncode)

        if proc_dict != None:
            proc_dict[os.getpid()] = False
        return proc.returncode

    def get_cnn_spider_data(self, search_term:str, sections:str, retry:bool = False, start_date: str = 'today', days_from_start_date: int = 1):
        return {
            'search_term': search_term,
            'sections': sections,
            'retry': retry,
            'start_date': start_date,
            'days_from_start_date': days_from_start_date
            }