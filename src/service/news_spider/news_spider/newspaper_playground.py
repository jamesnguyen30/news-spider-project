from newspaper import Article, Config
import requests
from bs4 import BeautifulSoup
import re
import sys

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'

link = 'https://www.cnn.com/2022/05/15/business/elon-musk-twitter-nda/index.html'

def manually_get_text(link):
    html = requests.get(link)

    soup = BeautifulSoup(html.text)

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

article = Article(link)
article.download()
article.parse()

text = article.text
last_line = text.split('\n')[-1]

if last_line == 'Read More':
    text = manually_get_text(link)
    article.text = text

print(text)

article.nlp()

print(f'url:{link}')
print(f'summary {article.summary}')
print(f'keywords: {article.keywords}')
print(f'top image:{article.top_image}')
print(f'authors:{article.authors}')
print(f'date:{article.publish_date}')
print(f'title:{article.title}')