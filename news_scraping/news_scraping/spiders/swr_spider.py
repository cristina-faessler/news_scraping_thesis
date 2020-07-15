import scrapy
from ..items import NewsScrapingItem

class RbbSpider(scrapy.Spider):

    name = 'swr_spider'
    start_urls = ['https://www.swr.de/swraktuell/swraktuell-100.html']

    def parse(self, response):
        selector = "article > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        headline = response.css('header > h1 > span:nth-child(2)::text').extract()
        date_publish = response.css('time > .date::text').extract()
        article_text = response.css('p::text').extract()
        link = response.url

        if date_publish is not None:
            date_publish = date_publish[0]

        article_text = list(map(lambda x: x.strip(), article_text))

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem