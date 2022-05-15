cd ./src/service/news_spider/news_spider
scrapy crawl cnn_search_spider -a search_term=tesla -a sections=business -a start_date=today -a days_from_start_date=5
# scrapy crawl cnn_search_spider -a search_term=tesla -a sections=business
#scrapy crawl cnn_search_spider -a search_term=microsoft -a sections=business
#scrapy crawl cnn_search_spider -a search_term=google -a sections=business
#scrapy crawl cnn_search_spider -a search_term=amazon -a sections=business
#scrapy crawl cnn_search_spider -a search_term=nvidia -a sections=business
#scrapy crawl cnn_search_spider -a search_term=amd -a sections=business

