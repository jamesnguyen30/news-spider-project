from news_db import NewsDb
from db.schemas import News 
from datetime import datetime
import unittest

class TestNewsDatabase(unittest.TestCase):

    def test_save(self):
        controller = NewsDb()

        testdata = {
            'title': "something",
            'text': "text body here",
            'authors': ['John Lenon'],
            'source': 'CNN',
            'url': 'https://whatever',
            'image_url': 'https://whatever/image',
            'date': datetime.now()
        }

        testobject = controller.save(
            testdata['title'],
            testdata['text'],
            testdata['authors'],
            testdata['source'],
            testdata['url'],
            testdata['image_url'],
            testdata['date'],
        )

        loadnews = News.objects(id = testobject.id).first()
        self.assertTrue(loadnews.title == testdata['title'])

        controller.close()





