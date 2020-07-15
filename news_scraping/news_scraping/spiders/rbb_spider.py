import scrapy
from ..items import NewsScrapingItem

class RbbSpider(scrapy.Spider):

    name = 'rbb_spider'
    start_urls = ['https://www.rbb24.de/']

    def parse(self, response):
        selector = "article a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        if 'html' in response.url:
            headline = response.css('h3 > span.titletext::text').extract()
            date_publish = response.css('time::text').extract()
            article_text = response.css('.textblock p::text').extract()
            link = response.url

            date_publish = date_publish[0]
            headline = list(map(lambda x: x.strip(), headline))

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

            yield articleItem