import pandas as pd
from datetime import datetime
from collections import Counter
import os

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
        search_term: str
     ):
        '''
        add data to collected data
        '''
        if self._check_if_url_exists(url):
            return

        self.new_data.append([title, date, text, authors, source, url , image_url, search_term])
        self.counter_url[url]+=1

    def to_csv(self, output_filename):
        '''
        @return
            pandas.DataFrame
        '''
        new_df = pd.DataFrame(self.new_data, columns = ['title', 'date', 'text', 'authors', 'source', 'url', 'image_url', 'search_term'])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self.df.to_csv(output_filename, index = False)


