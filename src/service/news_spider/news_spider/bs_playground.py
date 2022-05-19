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



def _fetch_articles(link):
    # NOTE: newspaper can't parse date so timestamp was passed from html
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

    text += "#######\n"
    return text


if __name__ == '__main__':
    sample_file = os.path.join(CWD,'marketwatch_search.html' )

    link = 'https://www.reuters.com/site-search/?query=apple&section=business&offset=0'
    response = requests.get(link)

    html = response.text

    with open('saved.html', 'w') as file:
        file.write(html)


