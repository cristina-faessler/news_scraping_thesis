import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import NewsScrapingItem
import re
import spacy
from string import punctuation
from gensim.summarization.summarizer import summarize
from collections import Counter

class NdrSpider(scrapy.Spider):

    name = 'ndr_spider'
    start_urls = ['https://www.ndr.de/nachrichten/info/index.html']
    allowed_domains = ['ndr.de']
    nlp = spacy.load("de_core_news_lg")

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
        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        keywords = ''.join(top_key_words)
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

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(NdrSpider)
    process.start()
