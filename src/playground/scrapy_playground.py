import sys
import pathlib
import os

CWD = pathlib.Path(__file__).parent
SRC = pathlib.Path(__file__).parent.parent
sys.path.append(str(SRC))

OUTPUT = os.path.join(CWD, 'output')

try:
    os.mkdir(OUTPUT)
except Exception as e:
    print(str(e))

import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from service.news_spider.news_spider.spiders.CNNBusinessHeadlines import CNNBusinessHeadlines
from service.news_spider.news_spider.spiders.CNNSpider import CNNSpider 

if __name__ == '__main__':
    runner = CrawlerRunner() 
    runner.crawl(CNNBusinessHeadlines, sections='business', output_dir=OUTPUT)
    runner.crawl(CNNSpider, search_term="apple", sections='business', start_date="today", days_from_start_date=1)

    runner.join()
    # runner.start()

    print("End")
