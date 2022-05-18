from bs4 import BeautifulSoup as bs
from newspaper import Article
import pathlib
import os
import nltk
import uuid
import sys
from datetime import datetime, timedelta
import requests

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()

OUTPUT_DIR = os.path.join(CWD, 'dataset')
META_DIR = os.path.join(OUTPUT_DIR, 'metadata')

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
    os.mkdir(META_DIR)

print(f"Saving to {OUTPUT_DIR}")

def _process_html_from_path(html_path):
    with open(html_path, 'r') as file:
        html = file.read()
    
    soup = bs(html)

    article_divs = soup.find_all('div', {'class':'element--article'})

    valid_links = list()
    for div in article_divs:
        h3 = div.find('h3', {'class': 'article__headline'})
        href = h3.find('a', {'class': 'link'}).attrs['href']
        if href == '#':
            break
        timestamp = int(div.attrs['data-timestamp'])//1000
        valid_links.append({'timestamp': timestamp, 'link': href})
        print(valid_links[-1])
    
    print(f"Got {len(valid_links)} links")
    return valid_links

def _fetch_articles(data):
    # NOTE: newspaper can't parse date so timestamp was passed from html
    link = data['link']
    timestamp = data['timestamp']

    article = Article(link)

    article.download()
    article.parse()

    text = ''
    processed_text = ''

    #Process text
    for line in article.text.split("\n"):
        if line.startswith("Random reads") or line.startswith('Also read'):
            break
        if line == 'text None':
            break
        processed_text += line + '\n'
    article.text = processed_text

    text += f'link {link}\n'
    text += f'title {article.title}\n'
    text += f'text {article.text}\n'
    text += f'authors {article.authors}\n'
    text += f'date {datetime.fromtimestamp(timestamp)}\n'


    # text += f'summary {article.summary}\n'
    # text += f'keywords {article.keywords}\n'
    # text += f'top image {article.top_image}\n'
    # text += f'authors {article.authors}\n'
    # text += f'date {datetime.fromtimestamp(timestamp)}\n'

    text += "#######\n"
    return text


if __name__ == '__main__':
    sample_file = os.path.join(CWD,'marketwatch_search.html' )

    link = 'https://www.marketwatch.com/search?q=apple&ts=0&tab=All%20News&pageNumber=3'
    response = requests.get(link)

    html = response.text

    with open('saved.html', 'w') as file:
        file.write(html)

    links = _process_html_from_path('saved.html')

    text = list()
    for link in links:
        try:
            output = _fetch_articles(link)
            print(output)
            text.append(output)
            break
        except Exception as e:
            print(str(e))

    text = "\n".join(text)

    with open('format_test.txt', 'w') as file:
        file.write(text)
