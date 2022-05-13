from datetime import datetime
import mongoengine
from .config import *

class News(mongoengine.Document):
    meta = {
        'db_alias': TRENDING_DB_ALIAS,
        'collection': TRENDING_DB
    }

    date = mongoengine.DateTimeField(default = datetime.now())
    title = mongoengine.StringField(required = True)
    text = mongoengine.StringField(required = True)
    authors = mongoengine.ListField(required = True)
    source = mongoengine.StringField(required = True)
    url = mongoengine.StringField(required = True)
    image_url = mongoengine.StringField(default = None)