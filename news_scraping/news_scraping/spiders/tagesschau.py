# @author: Cristina Bolohan
import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess
from gensim.summarization.summarizer import summarize
import spacy
from string import punctuation
import re
from collections import Counter

class TagesschauSpider(scrapy.Spider):

    name = 'tagesschau'
    start_urls = ['https://www.tagesschau.de']
    allowed_domains = ['www.tagesschau.de']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav_bar_url = response.css(".ressorts > li > span a::attr('href')")
        items = nav_bar_url.extract()
        for page in items:
            next_page = response.urljoin(page)
            yield scrapy.Request(next_page, callback=self.get_all_links)

    def get_all_links(self, response):
        exclude = ['faktenfinder', 'multimedia', 'newsticker', 'regional', 'bab']
        article_container = "div.teaser > a::attr('href')"
        for href in response.css(article_container):
            url = response.urljoin(href.extract())
            if any(key_word in url for key_word in exclude):
                continue
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
        headline = response.css('.headline::text').extract()
        date_publish = response.css('span.stand::text').extract()
        article_text = response.css('p.text.small::text').extract()
        while '\n' in article_text: article_text.remove('\n')
        article_text = ''.join(article_text)
        author = response.css('p.autorenzeile.small::text').extract()
        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        keywords = ''.join(top_key_words)
        summary = summarize(article_text)
        subject = response.url.split('/')[3]
        link = response.url

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
    process.crawl(TagesschauSpider)
    process.start()
