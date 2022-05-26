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

def extract_links(html):
    soup = bs(html)

    all_a_tags = soup.find_all('a')
    hrefs = list()
    for a in all_a_tags:
        try:
            href = a.attrs['href']
            if href.endswith(f'index.html'):
                hrefs.append(href)

        except Exception as e:
            print(str(e))
            continue
    
    return hrefs


if __name__ == '__main__':
    with open('cnn_sample.html', 'r') as file:
        html = file.read()
    
    links = extract_links(html)
    for link in links:
        link = 'https://www.cnn.com'+link
        print(link)
        article = Article(link)
        article.download()
        article.parse()
        print(article.text)
        break





    

