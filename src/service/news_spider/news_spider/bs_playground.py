from functools import partial
from telnetlib import SE
from bs4 import BeautifulSoup as bs
from newspaper import Article
from datetime import datetime, timedelta
from GoogleNews import GoogleNews
import json 
from newsapi import NewsApiClient
import pathlib
import os
import requests
import re

SRC_DIR = pathlib.Path(__file__).parent.parent.parent.parent.absolute()
SECRET_DIR = os.path.join(SRC_DIR, 'secrets', 'newsapi_key.txt')

def news_api_playground():
    with open(SECRET_DIR, 'r') as file:
        apikey = file.readline()
    
    print(apikey)

    newsapi = NewsApiClient(api_key = apikey)

    headlines = newsapi.get_top_headlines(q='', category='business')
    print(headlines)

    with open('newsapi_result.json', 'w') as file:
        json.dump(headlines, file)

    # Process response from newsapi top headlines

    with open('newsapi_result.json', 'r') as file:
        headlines = json.load(file)

    # print(headlines) 
    print(headlines['status'])
    # print(headlines['articles'][0])
    error_links = list()

    for headline in headlines['articles']:
        try:
            article = Article(headline['url'])

            if headline['source']['name'] == 'CNBC':
                headline['content'] = cnbc_parser(headline['url'])

            else:
                article.download()
                article.parse()
                headline['content'] = article.text

            print(f"got content for {headline['title']}")
        except Exception as e:
            print(f" error link: {headline['url']}\n{str(e)}")
            error_links.append(headline['url'])
        
    print('Error links : ' + str(error_links))

    with open('newsapi_result_with_article.json', 'w') as file:
        json.dump(headlines, file)

def cnbc_parser(link):
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


if __name__ == '__main__':
    # googlenews = GoogleNews(lang = 'en', region = 'US')
    # googlenews.get_news("APPLE")
    # results = googlenews.results()
    # for result in results:
    #     print(result)

    # link = 'https://www.cnbc.com/2022/05/25/ripple-will-explore-ipo-after-sec-lawsuit-ends-ceo-says.html'
    # # link = 'https://www.cnbc.com/2022/05/25/try-these-gas-saving-tips-before-hitting-the-road-this-memorial-day-weekend.html'
    # link = 'https://www.cnbc.com/2022/05/25/5-things-to-know-before-the-stock-market-opens-wednesday-may-25.html'
    # link = 'https://www.cnbc.com/2022/05/25/stocks-making-the-biggest-moves-premarket-dicks-sporting-express-wendys-and-more.html'
    # link = 'https://www.cnbc.com/2022/05/25/ecb-member-knot-says-a-50-basis-point-hike-in-july-is-not-off-the-table.html'

    # text = cnbc_parser(link)
    # print(text)

    news_api_playground()








    

