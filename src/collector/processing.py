import pathlib
import sys 
import os
import pandas as pd

CWD = pathlib.Path(__file__).parent.absolute()

sys.path.append(str(CWD))

from nlp import entity_extractor, summarizer

class DataProcessor():
    '''
    Process news data using CSV format

    '''
    def __init__(self, csv_path):
        self.OUTPUT_DIR = os.path.join(CWD, 'output') 
        self.CSV_PATH = csv_path

        self.entity_extractor = entity_extractor.EntityExtractor(self.OUTPUT_DIR)
        self.trending_keyword_filename = self.entity_extractor.TRENDING_KEYWORDS_FILE
        self.summarizer = summarizer.SimpleSummarizer()
    

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

        for index, row in df.iterrows():
            if debug:
                print(f"Extracting keywords from {row['title']} and add summary")
            counter = self.entity_extractor.count_entities(row['text']) 
            keywords = list()
            for key, value in counter.most_common():
                keywords.append(key)
            
            summary = self.summarizer.summarize(row['text'])

            df.at[index, 'keywords'] = ','.join(keywords)
            df.at[index, 'summary'] = summary

        print(df.loc[:])
        
        df.to_csv(csv_path)
    
    def produce_trending_keywords(self):
        self.entity_extractor.get_trending_keywords(self.CSV_PATH, True)
        self.entity_extractor.save_trending_keywords()


