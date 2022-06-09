import requests
from dotenv import load_dotenv
import os
import pathlib
import json
from datetime import datetime

class NewsService():
    SRC = pathlib.Path(__file__).parent.parent.parent
    DOTENV_PATH = os.path.join(SRC, 'secrets', 'dotenv')
    DOTENV_PATH = '/home/nguyen/Desktop/news_spider_project/src/secrets/dotenv'

    if os.path.exists(DOTENV_PATH) == False:
        raise Exception('dotenv is not found. abort')

    load_dotenv(DOTENV_PATH)
    NEWS_SERVICE_IP = os.getenv("NEWS_SERVICE_IP")
    NEWS_SERVICE_PORT = os.getenv("NEWS_SERVICE_PORT")
    NEWS_SERVICE_PROTOCOL = os.getenv("NEWS_SERVICE_PROTOCOL")

    if NEWS_SERVICE_IP == None or NEWS_SERVICE_PORT == None or NEWS_SERVICE_PROTOCOL == None:
        raise Exception('PORT or IP, PORT variable is None, dotenv path is not setup correctly')

    def __init__(self):
        self.URL = f'{self.NEWS_SERVICE_PROTOCOL}://{self.NEWS_SERVICE_IP}:{self.NEWS_SERVICE_PORT}'
        print(self.URL)
    
    def check_health(self):
        response = requests.get(f'{self.URL}')
        return json.loads(response.content.decode('utf-8'))
    
    def save_news(self, search_term: str, title: str, \
        text: str, authors: list, source: str, url: str, image_url: str, date: datetime):
        news_data = {
            'search_term': search_term,
            'title': title, 
            'text': text, 
            'authors': authors, 
            'source': source,
            'url': url,
            'image_url': image_url,
            'date': date.isoformat() + 'Z'
        }

        response = requests.post(f'{self.URL}/news', json =  news_data)

        return response

# if __name__ == '__main__':
#     service = NewsService()
#     result = service.check_health()
#     print(result['message'])

#     response = service.save_news('test search term', 'test title', 'test text', ['author1', 'author2'], 'test_source', 'test_url', 'test_url_image', datetime.now())

#     print(response.content)

