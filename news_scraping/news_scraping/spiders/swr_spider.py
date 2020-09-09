# @author: Cristina Bolohan
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import NewsScrapingItem
import spacy
from string import punctuation
from gensim.summarization.summarizer import summarize
from collections import Counter

class SwrSpider(scrapy.Spider):

    name = 'swr_spider'
    start_urls = ['https://www.swr.de/swraktuell/swraktuell-100.html']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav_bar = response.css(".navbar-nav > li > a::attr('href')").extract()

        for item in nav_bar:
            url = response.urljoin(item)
            if "swraktuell" in url:
                yield scrapy.Request(url, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = "h2 > a::attr('href')"
        exclude = ['radio', 'wahl', 'newsletter', 'sendung', 'video', 'rueckschau']
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
        if "swraktuell" in response.url:
            headline = response.css("div > header > h1 > span[itemprop='headline']::text").extract()
            date_publish = response.css('time > .date::text').extract()
            if date_publish is not None:
                date_publish = date_publish[0]
            article_text = response.css('.bodytext p::text').extract()
            article_text = ''.join(article_text)
            subject = response.url.split('/')[4]
            author = response.css('footer > div > dl.meta-authors > dd::text').extract()
            author = list(map(lambda x: x.strip(), author))
            hot_words = self.get_hotwords(article_text)
            top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
            keywords = ''.join(top_key_words)
            summary = summarize(article_text)
            link = response.url

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           subject=subject, author=author, keywords=keywords, summary=summary, link=link)

            yield articleItem


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(SwrSpider)
    process.start()