from mongoengine import connect, connection
import pymongo


try:
    client = pymongo.MongoClient('mongodb://localhost:27017/?readPreference=primary&ssl=false')
    print(client.server_info())
except Exception as e:
    print(str(e))


