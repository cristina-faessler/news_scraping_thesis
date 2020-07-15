import scrapy
from ..items import NewsScrapingItem

class DwSpider(scrapy.Spider):

    name = 'dw_spider'
    start_urls = ['https://www.dw.com/de/themen/s-9077']

    def parse(self, response):
        anchor_selector = ".news a::attr('href')"
        for href in response.css(anchor_selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        headline = response.css('h1::text').extract()
        date_publish = response.css('ul.smallList li::text').extract_first().strip()
        article_text = response.css('div.longText p::text').extract()
        link = response.url

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem
