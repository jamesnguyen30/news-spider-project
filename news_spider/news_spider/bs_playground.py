from bs4 import BeautifulSoup as bs
from newspaper import Article
import pathlib
import os
import nltk
import uuid

nltk.download('punkt')

CWD = pathlib.Path(__file__).parent.absolute()

OUTPUT_DIR = os.path.join(CWD, 'dataset')
META_DIR = os.path.join(OUTPUT_DIR, 'metadata')

if os.path.exists(OUTPUT_DIR) == False:
    os.mkdir(OUTPUT_DIR)
    os.mkdir(META_DIR)

print(f"Saving to {OUTPUT_DIR}")


if __name__ == '__main__':
    with open('cnn_search_results.html', 'r') as file:
        html = file.read()
    
    soup = bs(html)

    h3_headlines = soup.find_all('h3', {'class': 'cnn-search__result-headline'})

    links = list()

    for h3 in h3_headlines:
        href = h3.find("a").attrs['href']
        links.append("https:" + href)

    print(links[0])

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