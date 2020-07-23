import scrapy
from ..items import NewsScrapingItem
import re

class RbbSpider(scrapy.Spider):

    name = 'rbb_spider'
    start_urls = ['https://www.rbb24.de/']
    allowed_domains = ['rbb24.de']

    def parse(self, response):
        nav_menu = response.css("#nav-top-container li a::attr('href')").extract()

        for link in nav_menu:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = ".teasercontent h3 a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if 'social-media' in url:
                continue
            yield scrapy.Request(url, callback=self.scrape_news_article)

    def scrape_news_article(self, response):
        if 'html' in response.url:
            headline = response.css('h3 > span.titletext::text').extract()
            date_publish = response.css('time::text').extract()
            date_publish = date_publish[0]
            article_text = response.css('.textblock p::text').extract()
            subject = response.url.split('/')[3]
            link = response.url

            headline = list(map(lambda x: x.strip(), headline))

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           subject=subject, link=link)

            yield articleItem