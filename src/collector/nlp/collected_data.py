import pandas as pd
from datetime import datetime
from collections import Counter
import os

# TODO: there's a duplicate file in spider/utils.py
# I don't want to mess up with the scrapy code for now so 
# I didn't touch that file. Need to refractor 

class CollectedData:

    def __init__(self, dataframe_path: str = None):
        '''
        Init CollectedData class
        '''
        self.new_data = list() 
        self.counter_url = Counter()

        if dataframe_path == None or os.path.exists(dataframe_path) == False:
            self.df = pd.DataFrame() 
            print("No CSV to load")
        else:
            self.df = pd.read_csv(dataframe_path)
            print("Loaded ")
            for index, row in self.df.iterrows():
                self.counter_url[row['url']]+=1
    
    def _check_if_url_exists(self, url):
        if url in self.counter_url:
            return True
        return False
    
    def add_data(self, 
        title: str, 
        text: str, 
        date: datetime, 
        authors: list, 
        source: str, 
        url: str, 
        image_url: str,
        search_term: str,
        summary = None,
        keywords = None
     ):
        '''
        add data to collected data
        '''
        if self._check_if_url_exists(url):
            return

        self.new_data.append([title, date, text, authors, source, url , image_url, search_term, summary, keywords])
        self.counter_url[url]+=1
    
    def get_new_row_count(self):
        return len(self.new_data)

    def get_total_row_count(self):
        return self.df.shape[0]

    def to_csv(self, output_filename, debug = False):
        '''
        @return
            pandas.DataFrame
        '''
        new_df = pd.DataFrame(self.new_data, columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url', 'search_term', 'summary', 'keywords'])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.df.to_csv(output_filename, index = False)

        if debug:
            print(f"CSV saved to {output_filename}")
