import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess
import re
from gensim.summarization.summarizer import summarize
import yake

class BRSpider(scrapy.Spider):

    name = 'br_spider'
    start_urls = ['https://www.br.de/nachrichten/']

    def parse(self, response):
        nav_bar_url = response.css("#__next > header > div.css-1rumvwz > nav > div > div.css-10gc1wg > div > ul > li > a::attr('href')")

        items = nav_bar_url.extract()

        for page in items:
            exclude = ['newsletter', 'meldungen', 'br24-zeitreise', 'fragbr24']
            next_page = response.urljoin(page)
            if any(key_word in next_page for key_word in exclude):
                continue
            articleItem = NewsScrapingItem()
            articleItem['subject'] = next_page.split('/')[4]
            articleItem['subject'] = articleItem['subject'].split(',')[0]
            request = scrapy.Request(next_page, callback=self.get_all_links)
            request.meta['item'] = articleItem  # By calling .meta, we can pass our item object into the callback.
            yield request

    def get_all_links(self, response):
        articleItem = response.meta['item']
        selector = "article > header > a:nth-child(1)::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if "nachrichten" in url:
                request = scrapy.Request(url, callback=self.scrape)
                request.meta['item'] = articleItem
                yield request

    def scrape(self, response):
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h3::text').extract()
        articleItem['date_publish'] = response.css("time::attr('title')").extract()
        articleItem['article_text'] = response.css('.css-1jftgse p::text').extract()
        article_text = ''.join(articleItem['article_text'])
        articleItem['author'] = response.css(".css-134vnn1 section:nth-child(3) li a span::text").extract()
        articleItem['author'] = ','.join(articleItem['author'])
        kw_extractor = yake.KeywordExtractor(lan='de', top=10)
        articleItem['keywords'] = kw_extractor.extract_keywords(article_text)
        articleItem['summary'] = summarize(article_text)
        articleItem['link'] = response.url

        if 'Sekundäre Navigation' in articleItem['headline']: articleItem['headline'].remove('Sekundäre Navigation')

        for i in articleItem['date_publish']:
            pattern = re.compile(r'\d{2}.\d{2}.\d{4}')
            result = re.search(pattern, i)
            articleItem['date_publish'] = result.group()

        yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BRSpider)
    process.start()