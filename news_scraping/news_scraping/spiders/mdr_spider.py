import scrapy
from ..items import NewsScrapingItem

class RbbSpider(scrapy.Spider):

    name = 'mdr_spider'
    start_urls = ['https://www.mdr.de/nachrichten/index.html']

    def parse(self, response):
        selector = "div > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        headline = response.css('h1 > span.headline::text').extract()
        date_publish = response.css('p.webtime > span::text').extract()
        article_text = response.css('.paragraph > .text::text').extract()
        link = response.url

        article_text = list(map(lambda x: x.strip(), article_text))

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem