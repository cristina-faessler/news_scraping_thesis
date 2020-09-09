# @author: Cristina Bolohan
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import NewsScrapingItem
import spacy
from string import punctuation
from gensim.summarization.summarizer import summarize
from collections import Counter

class DwSpider(scrapy.Spider):

    name = 'dw_spider'
    start_urls = ['https://www.dw.com/de/themen/s-9077']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav_menu = response.css("#navLevel2 > li > a::attr('href')")
        items = nav_menu.extract()

        for page in items:
            next_page = response.urljoin(page)
            articleItem = NewsScrapingItem()
            articleItem['subject'] = next_page.split('/')[5]
            request = scrapy.Request(next_page, callback=self.get_all_links)
            request.meta['item'] = articleItem  # By calling .meta, we can pass our item object into the callback.
            yield request

    def get_all_links(self, response):
        exclude = ['tv', 'g-', 'av-']
        articleItem = response.meta['item']
        anchor_selector = ".news a::attr('href')"
        for href in response.css(anchor_selector):
            url = response.urljoin(href.extract())
            if any(key_word in url for key_word in exclude):
                continue
            request = scrapy.Request(url, callback=self.parse_news_article)
            request.meta['item'] = articleItem
            yield request

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
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h1::text').extract()
        articleItem['date_publish'] = response.css('ul.smallList li::text').extract_first().strip()
        articleItem['article_text'] = response.css('div.longText p::text').extract()
        article_text = ''.join(articleItem['article_text'])
        articleItem['author'] = response.css('.group > .smallList > li:nth-child(2)::text').extract()
        articleItem['author'] = list(map(lambda x: x.strip(), articleItem['author']))
        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        articleItem['keywords'] = ''.join(top_key_words)
        articleItem['summary'] = summarize(article_text)
        articleItem['link'] = response.url

        yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(DwSpider)
    process.start()
