'''
A simple summarizer
'''
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest

class SimpleSummarizer():
    def __init__(self):
        pass

    def _clean_text(self, text):
        final = list() 
        for line in text.split("\n"):
            if line.startswith('Register now for FREE'):
                continue

            if line == "":
                continue
        
            final.append(line)

        return "\n".join(final)

    def summarize(self, text:str, per:float = 0.2):

        nlp = spacy.load('en_core_web_lg')
        doc = nlp(text)
        tokens = [token for token in doc]
        word_count = Counter()

        for token in tokens:
            word = token.text.strip()

            if word == '”':
                continue
            if word.lower() not in STOP_WORDS and word.lower() not in punctuation:
                word_count[word.lower()] += 1

        max_freq = max(word_count.values())
        #Normalize frequencies

        for word in word_count.keys():
            word_count[word] = word_count[word] / max_freq
        
        sentence_tokens = [sent for sent in doc.sents]

        # Count the score for each sentence
        sentence_scores = Counter()

        for sent in sentence_tokens:
            sent_text = sent.text.strip()
            if len(sent) < 10:
                continue
            for word in sent:
                if word.text.lower() in word_count.keys():
                    sentence_scores[sent_text] += word_count[word.text.lower()]


        # print(sentence_scores)
        n = int(len(sentence_tokens) * per)
        highscore_sentences = nlargest(n, sentence_scores, key = sentence_scores.get)
        final = [sentence.strip() for sentence in highscore_sentences if len(sentence) > 10]
        
        return '\n'.join(final)