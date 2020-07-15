import scrapy
from ..items import NewsScrapingItem

class BRSpider(scrapy.Spider):

    name = 'br_spider'
    start_urls = ['https://www.br.de/nachrichten/',]

    def parse(self, response):
        selector = "article > header > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):

        headline = response.css('h3::text').extract()
        date_publish = response.css("time::attr('title')").extract()
        article_text = response.css('.css-1jftgse p::text').extract()
        link = response.url

        if 'Sekundäre Navigation' in headline: headline.remove('Sekundäre Navigation')
        # if 'Hinweis:' in article_text[0]: article_text.remove(article_text[0])

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

        yield articleItem