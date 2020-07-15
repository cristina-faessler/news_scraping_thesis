import scrapy
from ..items import NewsScrapingItem

class TagesschauSpider(scrapy.Spider):

    name = 'tagesschau'
    start_urls = ['https://www.tagesschau.de/']

    def parse(self, response):
        for href in response.css("div.teaser > a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):

        headline = response.css('.headline::text').extract()
        date_publish = response.css('span.stand::text').extract()
        article_text = response.css('p.text.small::text').extract()
        link = response.url

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem
