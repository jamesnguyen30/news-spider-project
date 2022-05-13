commands:
scrapy crawl cnn_search_spider

-a search_term: pass in keyword to search, e.g: apple
-a sections: sections to filter out, 
    cnn search sections are:
        All CNN, World, Politics, Business, Opinions, Health, Entertainment, Style, Travel
-a retry: True or False to retry error links in previous fetch

