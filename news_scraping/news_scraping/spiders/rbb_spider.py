import scrapy
from ..items import NewsScrapingItem
import yake
from gensim.summarization.summarizer import summarize

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
            article_text = ''.join(article_text)
            kw_extractor = yake.KeywordExtractor(lan='de', top=10)
            keywords = kw_extractor.extract_keywords(article_text)
            author = ''
            subject = response.url.split('/')[3]
            summary = summarize(article_text)
            link = response.url

            headline = list(map(lambda x: x.strip(), headline))

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           author=author, subject=subject, keywords=keywords, summary=summary, link=link)


            yield articleItem