from datetime import datetime
import mongoengine
from pkg_resources import require

class Houses(mongoengine.Document):

    registered_date = mongoengine.DateTimeField(default=datetime.now)
    type = mongoengine.StringField(required=True)
    rooms = mongoengine.IntField(required=True)
    name = mongoengine.StringField(required=True)
    address = mongoengine.StringField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'houses'
    }