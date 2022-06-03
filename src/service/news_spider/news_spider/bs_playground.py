from asyncio import all_tasks
from bs4 import BeautifulSoup as bs
from newspaper import Article
from datetime import datetime, timedelta
# from GoogleNews import GoogleNews
import json 
from newsapi import NewsApiClient
import pathlib
import os
import requests
import json
import pandas as pd

CWD = pathlib.Path(__file__).parent

TMP_DIR = os.path.join(CWD, 'tmp')

if os.path.exists(TMP_DIR) == False:
    os.mkdir(TMP_DIR)

def get_marketwatch_latest_news():
    response = requests.get('https://www.marketwatch.com/latest-news?mod=home-page')

    html = str(response.content)

    tmp_file = os.path.join(TMP_DIR, 'marketwatch_headlines.html')

    with open(tmp_file, 'w') as file:
        file.write(html)
    
    soup = bs(html)

    article_contents = soup.find_all('div', {'class': 'article__content'})

    marketwatch_headlines = list()

    data = list()

    now = datetime.now()

    for div in article_contents:
        try:
            h3 = div.find("h3", {'class': 'article__headline'})
            href = h3.find("a", {'class': 'link'}).attrs['href']

            if href.startswith("https://www.marketwatch.com/"):
                # marketwatch_headlines.append(href)
                print(f"Extracting url: {href}")
                article = Article(href)
                article.download()
                article.parse()

                data.append(
                    {
                        'title': article.title,
                        'date': now,
                        'text': article.text,
                        'authors': article.authors,
                        'source': 'MarketWatch',
                        'url': href,
                        'image_url': article.top_image
                    }
                )

            else:
                continue

        except Exception as e:
            print(str(e))
        
    df = pd.DataFrame(data, columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url'])
    csv_output = os.path.join(TMP_DIR, 'marketwatch', )
    csv_path = os.path.join(csv_output, f'headlines_{now.month}_{now.day}_{now.year}.csv')
    if os.path.exists(csv_output) == False:
        os.mkdir(csv_output)

    df.to_csv(csv_path)

    print("Saved to df")

def parse_cnn(link):
    html = requests.get(link)

    soup = bs(html.text)

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


if __name__ == '__main__':

    response = requests.get('https://www.reuters.com/business/')

    html = response.content

    soup = bs(html)

    print()




    

    


