# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScrapingItem(scrapy.Item):
    headline = scrapy.Field()
    date_publish = scrapy.Field()
    article_text = scrapy.Field()
    author = scrapy.Field()
    keywords = scrapy.Field()
    summary = scrapy.Field()
    subject = scrapy.Field()
    link = scrapy.Field()

