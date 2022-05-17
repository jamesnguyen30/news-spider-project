from newspaper import Article
# link = 'https://www.bloomberg.com/news/articles/2022-05-17/elon-musk-says-twitter-must-prove-bot-claims-for-deal-to-proceed?srnd=premium'
# link = 'https://www.barrons.com/articles/buy-citizens-financial-stock-pick-51652337002?mod=hp_StockPicks'
# link = 'https://www.cnbc.com/2022/05/17/walmart-wmt-earnings-q1-2023.html'
# link = 'https://www.cnbc.com/2022/05/17/retail-sales-april-2022-up-0point9percent-vs-1point0percent-estimate.html'

#MARKET WATCH
# link = 'https://www.marketwatch.com/story/remote-work-has-fueled-u-s-house-prices-during-the-pandemic-so-what-happens-when-people-return-to-the-office-11652761085?mod=personal-finance'
# link = 'https://www.marketwatch.com/articles/stock-market-sp-500-outlook-51652197922?mod=moremw_bomw'
link = 'https://www.marketwatch.com/story/the-beginning-of-the-end-of-the-stock-markets-correction-could-be-near-11652397281?mod=markets&tesla=y'
link = 'https://www.marketwatch.com/story/oil-prices-come-under-renewed-pressure-as-market-looks-for-direction-11652359238?mod=markets'
link ='https://www.marketwatch.com/story/remote-work-has-fueled-u-s-house-prices-during-the-pandemic-so-what-happens-when-people-return-to-the-office-11652761085?mod=search_headline'
link = 'https://www.marketwatch.com/story/the-2022-honda-cr-v-hybrid-vs-the-toyota-rav4-hybridwhich-is-better-11652384034?mod=search_headline'
link = 'https://www.marketwatch.com/story/apple-inc-stock-falls-monday-still-outperforms-market-01652733112-fb207af3f714?mod=search_headline'
link = 'https://www.marketwatch.com/story/alphabet-inc-cl-a-stock-underperforms-monday-when-compared-to-competitors-01652733111-db387b3f91f2?mod=search_headline'

#bloomber, can't download, must have javascript enabled
# link = 'https://www.bloomberg.com/news/articles/2022-05-16/asia-stocks-set-for-cautious-open-on-growth-worry-markets-wrap?srnd=premium'

article = Article(link) 

article.download()
article.parse()

print(article.text)