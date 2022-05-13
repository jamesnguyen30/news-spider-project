from datetime import datetime
from email.policy import default
import mongoengine

class Bookings(mongoengine.EmbeddedDocument):

    owner_id = mongoengine.ObjectIdField()
    

    booked_date = mongoengine.DateTimeField(default = datetime.now)
    checkin_date = mongoengine.DateTimeField(required=True)
    checkout_date = mongoengine.DateTimeField(required=True)
    review = mongoengine.StringField()
    rating = mongoengine.IntField(default = 1)

    meta = {
        'db_alias': 'core',
        'collection': 'bookings'
    }