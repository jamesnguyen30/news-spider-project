import re


a = 'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query=%7B%22keyword%22%3A%22apple%22%2C%22offset%22%3A10%2C%22orderby%22%3A%22display_date%3Adesc%22%2C%22sections%22%3A%22%2Fbusiness%22%2C%22size%22%3A10%2C%22website%22%3A%22reuters%22%7D&d=95&_website=reuterssub'


a = re.sub('%7B', '{', a)
a = re.sub('%7D', '}', a)
a = re.sub('%22', '"', a)
a = re.sub('%3A', ':', a)
a = re.sub('%2C', ',', a)
a = re.sub('%2F', '/', a)

print(a)
