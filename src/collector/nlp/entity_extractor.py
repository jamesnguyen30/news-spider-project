import nltk
from nltk.corpus import stopwords
from collections import Counter
from numpy import extract
import pandas as pd
import spacy
from spacy import displacy
import pathlib
import os
from datetime import datetime

nltk.download('stopwords')

# Remember to run this command before running Extractor
# python3 -m spacy download en_core_web_lg

nlp = spacy.load('en_core_web_lg')
CWD = pathlib.Path(__file__).parent


class EntityExtractor():

    def __init__(self, output_dir, trending_keyword_filename=None):
        print("Created EntityExtractor")

        now = datetime.now()
        self.DEFAULT_TRENDING_FILENAME = f'trending_{now.month}_{now.day}_{now.year}.txt'

        if trending_keyword_filename == None:
            trending_keyword_filename = self.DEFAULT_TRENDING_FILENAME

        self.OUTPUT_DIR = output_dir
        self.TRENDING_KEYWORDS_FILE = os.path.join(
            self.OUTPUT_DIR, trending_keyword_filename)
        self.IGNORE_ENTITIES_FILE = os.path.join(CWD, 'ignore_keywords.txt')
        self.INTERESTED_ENTITY_FILE = os.path.join(
            CWD, 'interested_entity.txt')
        self.HEADLINE_FILE = os.path.join(
            self.OUTPUT_DIR, f'headlines_{now.month}_{now.day}_{now.year}.csv')

        try:
            self.INTERESTED_ENTITY = list()
            with open(self.INTERESTED_ENTITY_FILE, 'r') as file:
                for line in file.readlines():
                    if(line.startswith("#") == False):
                        self.INTERESTED_ENTITY.append(line.lower().strip())
        except Exception as e:
            print("Can't load interested entity file, setting ignore entity to default")
            print(str(e))

        try:
            self.IGNORE_ENTITY = list()
            with open(self.IGNORE_ENTITIES_FILE, 'r') as file:
                for line in file.readlines():
                    if(line.startswith("#") == False):
                        self.IGNORE_ENTITY.append(line.lower().strip())

        except Exception as e:
            print("Can't load ignore entity file, setHEADting ignore entity to default")
            print(str(e))

        print('ignore keywords ', self.IGNORE_ENTITY)
        print('interested entity', self.INTERESTED_ENTITY)

    def count_entities(self, text, counter: Counter = None, debug=False) -> Counter:
        '''
        given a text of an article, extract entities
        @params:
            string text: body text of the article
            collections.Counter counter = None: pass in a counter object to prevent duplication
            boolean debug = False: print debug messages if set to True
        @return
            collections.Counter
        '''
        doc = nlp(text)

        if debug:
            displacy.render(doc, style='ent')

        if counter == None:
            counter = Counter()

        # Only count the entity once for every article
        seen_entity = Counter()

        for entity in doc.ents:
            label = entity.label_.lower()
            text = entity.text.lower().strip()
            if label in self.INTERESTED_ENTITY and text not in self.IGNORE_ENTITY and text not in seen_entity:
                counter[text] += 1
                seen_entity[text] += 1
        return counter

    def generate_trending_keywords(self, csv_path = None, debug=False):
        '''
        Traverse through a dataframe and produce counter object
        self.trending will be reset
        @params:
            string csv_path: path to csv file default will bet set to self.HEADLINE_FILE path
            boolean debug = False: print messages if set to True
        @returns
            self.trending_keywords instance
        '''
        if csv_path == None:
            csv_path = self.HEADLINE_FILE

        self.trending_keywords = Counter()
        try:
            df = pd.read_csv(csv_path)
            # df = df.dropna()
            df = df[df['text'].notna()]

            if debug:
                print("Dataframe heads")
                print(df.head())
                print("Dataframe info")
                print(df.info())
                print(f"Processing {len(df['title'])} rows")

            for index, row in df.iterrows():
                if row['text'] == 'NaN' or row['text'] == '':
                    print(f"Empty text content, skipping this {row['title']}")
                    continue

                print(f"extracting index: {index}, {row['title']}")
                try:
                    self.trending_keywords = self.count_entities(
                        row['text'], counter=self.trending_keywords, debug=debug)

                except Exception as e:
                    print('ERROR ROW ', row)
                    print(e)

        except Exception as e:
            print(str(e))

        finally:
            return self.trending_keywords

    def load_trending_keywords(self):
        '''
        Read from keyword file and return list of keywords and its rank
        @return 
            list keywords: [(key, value)]
        '''
        keywords = Counter()
        try:
            with open(self.TRENDING_KEYWORDS_FILE, 'r') as file:
                for line in file.readlines():
                    key, value = line.split(":")
                    value = int(value)
                    keywords[key] = value
                self.trending_keywords = keywords
                return self.trending_keywords

        except FileNotFoundError as e:
            print("Trendiing keywords file not found, returning empty list")
            print(str(e))
            return None

    def save_trending_keywords(self, min_count=2):
        '''
        @params:
            int min_count: minimum count of a keyword to be saved
        '''
        try:
            with open(self.TRENDING_KEYWORDS_FILE, 'w') as file:
                for key, value in self.trending_keywords.most_common():
                    if value >= min_count:
                        file.write(f'{key}:{value}\n')
        except Exception as e:
            print("Error occured while saving counter")
            print(str(e))
