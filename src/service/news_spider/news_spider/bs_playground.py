from bs4 import BeautifulSoup as bs
from newspaper import Article
import pathlib
import os
import nltk
import uuid
import sys
from datetime import datetime, timedelta
import requests
import json 

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()

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

def parse_article(article):
    authors = list()
    for author in article['authors']:
        authors.append(author['name'])

    data = {
        'title': article['title'],
        'description': article['description'],
        'published_date': article['display_time'],
        'url': f"https://www.reuters.com{article['canonical_url']}",
        'authors': authors
    }

    return data


if __name__ == '__main__':
    link = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query={"keyword":"apple","offset":10,"orderby":"display_date:desc","sections":"/business","size":10,"website":"reuters"}&d=95&_website=reuters'
    response = requests.get(link)
    res = response.text
    parsed = json.loads(res)

    print(f'status code {str(parsed["statusCode"])}')
    articles = parsed['result']['articles'] 
    print(f'articles count {len(articles)}')

    to_save = list()

    for article in articles:
        data = parse_article(article)
        article = Article(data['url'])
        article.download()
        article.parse()

        data['text'] = article.text
        data['top_image'] = article.top_image
        data['publish_date'] = article.publish_date

        print('Extracted data ' + str(data))

        to_save.append(data)

    save_file = os.path.join(CWD, 'saved.txt')
    with open(save_file, 'w') as file:
        for t in to_save:
            file.write(str(t) + '\n')
        
    

