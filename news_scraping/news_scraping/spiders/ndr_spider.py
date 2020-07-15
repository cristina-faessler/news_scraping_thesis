import scrapy
from ..items import NewsScrapingItem

class RbbSpider(scrapy.Spider):

    name = 'ndr_spider'
    start_urls = ['https://www.ndr.de/nachrichten/info/index.html']

    def parse(self, response):
        selector = "h2 > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        headline = response.css('h1::text').extract()
        date_publish = response.css('.lastchanged::text').extract()
        article_text = response.css('p::text').extract()
        link = response.url

        headline = list(map(lambda x: x.strip(), headline))
        date_publish = list(map(lambda x: x.strip(), date_publish))

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem
