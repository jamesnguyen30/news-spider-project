import subprocess
import pathlib
import os
CWD = pathlib.Path(__file__).parent.parent.parent.absolute()
SPIDER_DIR = os.path.join(CWD, 'news_spider', 'news_spider')

class CnnCrawler():
    def __init__(self):
        pass

    def run_search_process(self, search_term, sections, retry = False):
        try:
            cmd = f'scrapy crawl {spider} -a search_term={search_term} -a sections={sections} -a retry={retry}'
            spider = 'cnn_search_spider'
            subprocess.run(cmd, cwd = SPIDER_DIR, shell=True)
            return True
        except Exception:
            raise Exception
    