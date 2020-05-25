#extracted Data - Temporary containers (items) - storing in database
import scrapy
from urllib.parse import urljoin
from ..items import NewsScrapingItem

class NewsSpider(scrapy.Spider):

    name = 'news'
    start_urls = ['https://www.tagesschau.de/',]

    #parse function
    def parse(self, response):
        anchor_selector = "div.teaser > a::attr('href')"
        for href in response.css(anchor_selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
            items = NewsScrapingItem()

            headline = response.css('.headline::text').extract()
            date_publish = response.css('.stand').get()
            article_text = response.css('p.text.small::text').extract()

            items['headline'] = headline
            items['date_publish'] = date_publish
            items['article_text'] = article_text

            yield items