import scrapy
from ..items import NewsScrapingItem

class DFSpider(scrapy.Spider):

    name = 'df_spider'
    start_urls = ['https://www.deutschlandfunk.de/die-nachrichten.1441.de.html']

    def parse(self, response):

        anchor_selector = "article a::attr('href')"
        sel = "div.articlemain p a::attr('href')"

        for href in response.css(sel):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_article)

        for href in response.css(anchor_selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_article(self, response):
        headline = response.css('h1::text').extract()
        date_publish = response.css('span.current::text').extract()
        article_text = response.css('.text p::text').extract()
        link = response.url

        while '\n' in headline: headline.remove('\n')

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem

    def parse_news_article(self, response):

        headline = response.css('h1::text').extract()
        date_publish = response.css('time::text').extract()
        article_text = response.css('div.articlemain > p::text').extract()
        link = response.url

        while '\n' in headline: headline.remove('\n')

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem
