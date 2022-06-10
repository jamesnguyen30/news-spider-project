import pathlib
import sys 
import os
import pandas as pd
from nlp.sentiment.models import SentimentModel
from collections import Counter

CWD = pathlib.Path(__file__).parent.absolute()

sys.path.append(str(CWD))

from nlp import entity_extractor, summarizer

class DataProcessor():
    '''
    Process news data using CSV format

    '''
    def __init__(self):
        self.OUTPUT_DIR = os.path.join(CWD, 'output') 
        # self.CSV_PATH = csv_path

        self.entity_extractor = entity_extractor.EntityExtractor(self.OUTPUT_DIR)
        # self.trending_keyword_filename = self.entity_extractor.TRENDING_KEYWORDS_FILE
        self.summarizer = summarizer.SimpleSummarizer()
        self.sentiment_estimator = SentimentModel()
    
    def get_today_headlines_file(self):
        return self.entity_extractor.HEADLINE_FILE
    
    def process_data(self, csv_path, debug = False):
        '''
        Process fetched data
            1. extract keywords
            2. add summary 
            3. sentiment analysis by title

        @params:
            str cvs_path: path to csv file to save 
            boolean debug: print message if True
        
        @return 
            None
        '''
        df = pd.read_csv(csv_path)
        df.drop_duplicates(inplace=True)

        for index, row in df.iterrows():
            print(f"Extracting keywords and summary for {row['title']}")
            if debug:
                print(f"Extracting keywords from {row['title']} and add summary")
            counter = self.entity_extractor.count_entities(row['text']) 
            keywords = list()
            for key, value in counter.most_common():
                keywords.append(key)
            
            summary = self.summarizer.summarize(row['text'])

            df.at[index, 'keywords'] = ','.join(keywords)
            df.at[index, 'summary'] = summary

        print(f"Predicing title sentiment on data")
        #prepare for title sentiment predictions
        titles_array = df['title'].values
        titles = list()
        for title in titles_array:
            title = str(title)
            titles.append(title)

        labels = self.predict_titles_sentiment(titles)

        label_counter = Counter()
        for label in labels:
            label_counter[label] += 1

        print("Label statistics")
        print(label_counter)

        df['sentiment'] = labels 

        df.to_csv(csv_path)
    
    def predict_titles_sentiment(self, titles: list) -> list:
        results = self.sentiment_estimator.predict(titles)
        return results

    def generate_trending_keywords(self, csv_path = None):
        self.entity_extractor.generate_trending_keywords(csv_path, True)
        print(f"Extracted trending keywords")
        self.entity_extractor.save_trending_keywords()
    
    def get_trending_keyword(self):
        return self.entity_extractor.load_trending_keywords()

# if __name__ == '__main__':
#     processsor = DataProcessor('/home/nguyen/Desktop/news_spider_project/src/collector/output/headlines_6_9_2022.csv')

#     processsor.process_data('/home/nguyen/Desktop/news_spider_project/src/collector/output/headlines_6_9_2022.csv')

#     print('data is processed')
    # df = pd.read_csv('/home/nguyen/Desktop/news_spider_project/src/collector/output/headlines_6_9_2022.csv')

    # df.drop_duplicates(inplace=True)

    # titles_array = df['title'].values
    # titles = list()
    # for title in titles_array:
    #     title = str(title)
    #     title = title.split('-')[0]
    #     title = title.strip()
    #     titles.append(title)

    # labels = processsor.predict_titles_sentiment(titles)

    # for title, label in zip(titles, labels):
    #     print(f'{title}: {label}')


