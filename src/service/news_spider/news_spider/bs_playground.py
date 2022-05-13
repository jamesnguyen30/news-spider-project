from bs4 import BeautifulSoup as bs
from newspaper import Article
import pathlib
import os
import nltk
import uuid
import sys
from datetime import datetime, timedelta

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()

OUTPUT_DIR = os.path.join(CWD, 'dataset')
META_DIR = os.path.join(OUTPUT_DIR, 'metadata')

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
    os.mkdir(META_DIR)

print(f"Saving to {OUTPUT_DIR}")

if __name__ == '__main__':
    start_date = datetime.now()
    length = 1
    end_date = start_date - timedelta(days = length + 1)
    end_date = end_date.replace(hour = 23, minute = 59, second = 59)
    print('end date = ', end_date)

    sample_file = os.path.join(CWD,'sample_cnn_search_page.html' )
    with open(sample_file, 'r') as file:
        html = file.read()
    
    soup = bs(html)

    result_contents = soup.find_all('div', {'class':'cnn-search__result-contents'})

    links = list()

    for div in result_contents:
        href = div.find("h3", {'class': 'cnn-search__result-headline'}).find('a').attrs['href']
        date = div.find('div', {'class': 'cnn-search__result-publish-date'}).find_all('span')[1].text
        date_obj = datetime.strptime(date, "%b %d, %Y")
        print(date_obj, f"if {date_obj} > {end_date}: {date_obj > end_date}")
        links.append("https:" + href)

    print(links[0])

    sys.exit(0)

    for link in links:
        article = Article(link)
        article.download()
        article.parse()
        id = str(uuid.uuid4())
        extension = 'txt'
        filename = f'{id}_{article.title}.{extension}'
        with open(os.path.join(OUTPUT_DIR, filename), 'w') as file:
            file.write(article.text)
        print(f'body: {article.text}')

        meta_content = list() 
        article.nlp()
        meta_content.append(f'url:{link}')
        meta_content.append(f'summary:{article.summary}')
        meta_content.append(f'keywords:{article.keywords}')
        meta_content.append(f'top image:{article.top_image}')
        meta_content.append(f'authors:{article.authors}')
        meta_content.append(f'date:{article.publish_date}')
        meta_content.append(f'title:{article.title}')

        print('\n'.join(meta_content))

        meta_filename = f'{id}.{extension}'
        with open(os.path.join(META_DIR, meta_filename), 'w') as file:
            file.write('\n'.join(meta_content))

        # with open(os.path.join(OUTPUT_DIR, ), )