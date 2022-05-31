import nltk
from nltk.corpus import stopwords
from collections import Counter
from numpy import extract
import pandas as pd
import spacy
from spacy import displacy
import pathlib
import os

nltk.download('stopwords')

# Remember to run this command before running Extractor
# python3 -m spacy download en_core_web_lg

nlp = spacy.load('en_core_web_lg')

CWD = pathlib.Path(__file__).parent

class EntityExtractor():
    def __init__(self):

        self.COUNTER_FILE = os.path.join(CWD, 'trending.txt')
        self.IGNORE_ENTITIES_FILE = os.path.join(CWD, 'ignore_entity.txt')
        self.INTERESTED_ENTITY_FILE = os.path.join(CWD, 'interested_entity.txt')
        self.HEADLINE_FILE = os.path.join(CWD, 'headlines.csv')

        try:
            self.INTERESTED_ENTITY = list()
            with open(self.INTERESTED_ENTITY_FILE, 'r') as file:
                for line in file.readlines():
                    if(line.startswith("#") == False):
                        self.INTERESTED_ENTITY.append(line)
        except Exception as e:
            print("Can't load interested entity file, setting ignore entity to default")
            print(str(e))
        
        try:
            self.IGNORE_ENTITY = list()
            with open(self.IGNORE_ENTITIES_FILE, 'r') as file:
                for line in file.readlines():
                    if(line.startswith("#") == False):
                        self.IGNORE_ENTITY.append(line)

        except Exception as e:
            print("Can't load ignore entity file, setHEADting ignore entity to default")
            print(str(e))

        print('ignore keywords ', self.IGNORE_ENTITY)
        print('interested entity' , self.INTERESTED_ENTITY)

    def count_entities(self, text, counter = None, debug = False):
        doc = nlp(text)

        if debug:
            displacy.render(doc, style = 'ent')

        if counter == None:
            counter = Counter()

        # Only count the entity once for every article
        seen_entity = Counter()

        for entity in doc.ents:
            if entity.label_ in self.INTERESTED_ENTITY and entity.text not in self.IGNORE_ENTITY and entity.text not in seen_entity:
                counter[entity.text] +=1
                seen_entity[entity.text] +=1
        return counter        
    
    def process_data(self, csv_path, debug = False):
        try:
            df = pd.read_csv(csv_path)
            df = df.dropna()

            if debug:
                print("Dataframe heads")
                print(df.head())
                print("Dataframe info")
                print(df.info())
                print(f"Processing {len(df['title'])} rows")
            
            counter = Counter()

            counter = self.count_entities(df['text'][10], counter = counter)

            for index, row in df.iterrows():
                if row['text'] == 'NaN' or row['text'] == '':
                    print(f"Empty text content, skipping this {row['title']}")
                    continue
                
                print(f"extracting index: {index}, {row['title']}")
                try:
                    counter = self.count_entities(row['text'], counter = counter, debug=debug)
                except Exception as e:
                    print('ERROR ROW ', row)
                    print(e)
            self.counter = counter
            return counter

        except Exception as e:
            print(str(e))
            return None
    
    def save_counter(self, min_count = 2):
        if self.counter != None:
            with open(self.COUNTER_FILE, 'w') as file:
                for key, value in self.counter.most_common():
                    if value >= min_count:
                        file.write(f'{key}:{value}\n')
    
if __name__ == '__main__':
    extractor = EntityExtractor()
    counter =  extractor.process_data(extractor.HEADLINE_FILE, True)

    extractor.save_counter()


