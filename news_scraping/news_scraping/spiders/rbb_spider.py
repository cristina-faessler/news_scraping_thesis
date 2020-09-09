# @author: Cristina Bolohan
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import NewsScrapingItem
import spacy
from string import punctuation
from gensim.summarization.summarizer import summarize
from collections import Counter

class RbbSpider(scrapy.Spider):

    name = 'rbb_spider'
    start_urls = ['https://www.rbb24.de/']
    allowed_domains = ['rbb24.de']
    nlp = spacy.load("de_core_news_lg")

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

    def get_hotwords(self, text):
        result = []
        pos_tag = ['PROPN', 'NOUN']
        doc = self.nlp(text.lower())
        for token in doc:
            if (token.text in self.nlp.Defaults.stop_words or token.text in punctuation):
                continue
            if (token.pos_ in pos_tag):
                result.append(token.text)
        return result

    def scrape_news_article(self, response):
        if 'html' in response.url:
            headline = response.css('h3 > span.titletext::text').extract()
            date_publish = response.css('time::text').extract()
            date_publish = date_publish[0]
            article_text = response.css('.textblock p::text').extract()
            article_text = ''.join(article_text)
            hot_words = self.get_hotwords(article_text)
            top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
            keywords = ''.join(top_key_words)
            author = ''
            subject = response.url.split('/')[3]
            summary = summarize(article_text)
            link = response.url

            headline = list(map(lambda x: x.strip(), headline))

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           author=author, subject=subject, keywords=keywords, summary=summary, link=link)


            yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(RbbSpider)
    process.start()