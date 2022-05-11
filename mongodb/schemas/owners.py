from datetime import datetime
from bookings import Bookings
import mongoengine

class Owners(mongoengine.Document):

    registered_date = mongoengine.DateTimeField(default=datetime.now)
    name = mongoengine.StringField(required=True)

    house_ids = mongoengine.ListField()

    bookings = mongoengine.EmbeddedDocumentListField(Bookings)

    meta = {
        'db_alias': 'core',
        'collection': 'owners'
    }