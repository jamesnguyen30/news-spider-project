from .db.schemas import News
from .db import config
from mongoengine import connect, disconnect

class NewsDb():

    def __init__(self):
        self.init_db(config.TRENDING_DB_ALIAS, config.TRENDING_DB)

    def init_db(self, alias, name):
        connect(alias = alias, name = name)


    def save(self, title, text, authors, source, url, \
        image_url = None, published_date = None) -> bool: 

        to_save = News()
        if published_date != None:
            to_save.date = published_date 
        
        to_save.title = title 
        to_save.text = text 
        to_save.authors = authors
        to_save.source = source
        to_save.url = url
        to_save.image_url = image_url

        to_save.save()

        return to_save
    
    def get_by_id(id):
        news = News.objects(id = id)
        return news
    
    def get_by_title(title):
        news = News.objects(title = title)
        return news

    def close(self):
        disconnect()
