# @author: Cristina Bolohan
import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess
from gensim.summarization.summarizer import summarize
import spacy
from string import punctuation
from collections import Counter

class DFSpider(scrapy.Spider):

    name = 'df_spider'
    start_urls = ['https://www.deutschlandfunk.de/die-nachrichten.1441.de.html']
    allowed_domains = ['deutschlandfunk.de']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav_menu = response.css(".dlfn-main__nav > li > a::attr('href')")
        items = nav_menu.extract()
        count = 0
        for page in items:
            next_page = response.urljoin(page)
            articleItem = NewsScrapingItem()
            subject_sel = response.css(".dlfn-main__nav > li > a::text").extract()
            articleItem['subject'] = subject_sel[count]
            count += 1

            request = scrapy.Request(next_page, callback=self.get_all_links)
            request.meta['item'] = articleItem  # By calling .meta, we can pass our item object into the callback.
            yield request

    def get_all_links(self, response):
        articleItem = response.meta['item']
        selector = "article a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            request = scrapy.Request(url, callback=self.scrape)
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

    def scrape(self, response):
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h1::text').extract()
        articleItem['date_publish'] = response.css('time::text').extract()
        articleItem['article_text'] = response.css('.articlemain > p::text').extract()
        article_text = ''.join(articleItem['article_text'])
        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        articleItem['keywords'] = ''.join(top_key_words)
        articleItem['summary'] = summarize(article_text, ratio=0.2)
        articleItem['author'] = ''
        articleItem['link'] = response.url

        while '\n' in articleItem['headline']: articleItem['headline'].remove('\n')

        yield articleItem


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(DFSpider)
    process.start()


