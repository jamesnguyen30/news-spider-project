from .news_db import NewsDb
from .db.schemas import News 
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

        controller.delete(testobject)

        #Delete that data
        controller.close()
    
    def test_get_by_title(self):
        controller = NewsDb()

        test_title = 'test_title'

        testdata = {
            'title': test_title,
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

        loadnews = News.objects(title = test_title).first()
        self.assertTrue(loadnews.title == test_title)

        controller.delete(testobject)
        controller.close()
    
    def test_nonexist_title(self):
        controller = NewsDb()

        test_title = 'this_test_title_should_not_exist'

        loadnews = controller.get_by_title(test_title)

        print(loadnews)
        self.assertTrue(loadnews == None)

        controller.close()




