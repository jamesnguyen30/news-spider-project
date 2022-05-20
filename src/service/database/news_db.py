from jmespath import search
from .db.schemas import News
from .db import config
from mongoengine import connect, disconnect
from datetime import datetime

class NewsDb():

    def __init__(self):
        self.init_db(config.NEWS_DB, config.NEWS_COLLECTION)

    def init_db(self, alias, name):
        connect(alias = alias, name = name)

    def save(self, search_term,  title, text, authors, source, url, \
        image_url, date) -> bool: 

        to_save = News()
        to_save.date = date 

        print("date = ", str(date))

        to_save.search_term = search_term 
        to_save.title = title 
        to_save.text = text 
        to_save.authors = authors
        to_save.source = source
        to_save.url = url
        to_save.image_url = image_url

        to_save.save()

        return to_save
    
    def get_by_id(self, id):
        news = News.objects(id = id)
        return news
    
    def get_by_title(self, title) -> News:
        news = News.objects(title = title).first()
        return news

    def delete(self, obj):
        obj.delete()

    def close(self):
        disconnect()
