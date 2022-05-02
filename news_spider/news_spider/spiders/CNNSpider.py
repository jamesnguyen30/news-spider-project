import scrapy
from scrapy_splash import SplashRequest

class CNNSpider(scrapy.Spider):

    name = 'cnn_crawler'

    def __init__(self, urls = None, *args, **kwargs):
        super(CNNSpider, self).__init__(*args, **kwargs)
        if urls == None:
            self.starting_urls = ['https://cnn.com']
        else:
            self.starting_urls = urls

    def start_requests(self):
        print('Crawling: ', self.starting_urls)
        for url in self.starting_urls:
            yield SplashRequest(url, callback = self.parse, args = {'wait': 0.5})
    
    def parse(self, response):
        filename = 'cnn_sample.html'
        with open(filename, 'wb') as file:
            file.write(response.body)
