import scrapy
from ..items import NewsScrapingItem
import re
import yake
from gensim.summarization.summarizer import summarize

class RbbSpider(scrapy.Spider):

    name = 'ndr_spider'
    start_urls = ['https://www.ndr.de/nachrichten/info/index.html']
    allowed_domains = ['ndr.de']

    def parse(self, response):
        nav_menu = response.css('nav > ul > li > a::attr(href)').extract()

        for link in nav_menu:
            exclude = ['wetter', 'verkehr', 'fernsehen', 'radio', 'ratgeber']
            url = response.urljoin(link)
            if any(key_word in url for key_word in exclude):
                continue
            yield scrapy.Request(url, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = "h2 > a::attr('href')"
        exclude = ['orchester', 'podcast', 'index', 'sendungen', 'tippspiel', 'info', 'newsletter', 'audio']
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if any(key_word in url for key_word in exclude):
                continue
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        headline = response.css('header > h1::text').extract()
        date_publish = response.css('.lastchanged::text').extract()
        article_text = response.css('p::text').extract()
        article_text = ''.join(article_text)
        if 'nachrichten' in response.url:
            subject = response.url.split('/')[4]
        else:
            subject = response.url.split('/')[3]
        author = ''
        kw_extractor = yake.KeywordExtractor(lan='de', top=10)
        keywords = kw_extractor.extract_keywords(article_text)
        summary = summarize(article_text)
        link = response.url

        headline = list(map(lambda x: x.strip(), headline))
        date_publish = list(map(lambda x: x.strip(), date_publish))

        for i in date_publish:
            pattern = re.compile(r'\d{2}.\d{2}.\d{4}')
            result = re.search(pattern, i)
            date_publish = result.group()

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                       author=author, keywords=keywords, summary=summary, subject=subject, link=link)
        yield articleItem
