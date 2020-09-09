# @author: Cristina Bolohan
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import NewsScrapingItem
from gensim.summarization.summarizer import summarize
import spacy
from string import punctuation
from collections import Counter

class MdrSpider(scrapy.Spider):

    name = 'mdr_spider'
    start_urls = ['https://www.mdr.de/nachrichten/index.html']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav = response.css(".level1 > li > a::attr('href')")
        nav_bar = nav.extract()

        for item in nav_bar:
            url = response.urljoin(item)
            if "panorama" in url:
                yield scrapy.Request(url, callback=self.get_all_links)


        nav_menu = response.css(".level1 > li > .level2 > li > a::attr('href')")
        items = nav_menu.extract()
        for page in items:
            exclude = ['podcast', 'chronik']
            next_page = response.urljoin(page)
            if any(key_word in next_page for key_word in exclude):
                continue
            yield scrapy.Request(next_page, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = ".teaser > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.scrape)

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

    def scrape(self, response):
        headline = response.css('h1 > span.headline::text').extract()
        date_publish = response.css('p.webtime > span::text').extract()
        if date_publish is not None:
            date_publish = date_publish[1].replace(',','')
        article_text = response.css('.paragraph > .text::text').extract()
        article_text = ''.join(article_text)
        author =  response.css('p.author::text').extract()
        subject = response.url.split('/')[4]
        link = response.url
        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        keywords = ''.join(top_key_words)
        summary = summarize(article_text)

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                       author=author, keywords=keywords, summary=summary, subject=subject, link=link)

        yield articleItem


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(MdrSpider)
    process.start()