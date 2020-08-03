import scrapy
from ..items import NewsScrapingItem
import yake
from gensim.summarization.summarizer import summarize

class DwSpider(scrapy.Spider):

    name = 'dw_spider'
    start_urls = ['https://www.dw.com/de/themen/s-9077']

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
        articleItem = response.meta['item']
        anchor_selector = ".news a::attr('href')"
        for href in response.css(anchor_selector):
            url = response.urljoin(href.extract())
            request = scrapy.Request(url, callback=self.parse_news_article)
            request.meta['item'] = articleItem
            yield request

    def parse_news_article(self, response):
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h1::text').extract()
        articleItem['date_publish'] = response.css('ul.smallList li::text').extract_first().strip()
        articleItem['article_text'] = response.css('div.longText p::text').extract()
        article_text = ''.join(articleItem['article_text'])
        articleItem['author'] = response.css('.group > .smallList > li:nth-child(2)::text').extract()
        articleItem['author'] = list(map(lambda x: x.strip(), articleItem['author']))
        kw_extractor = yake.KeywordExtractor(lan='de', top=10)
        articleItem['keywords'] = kw_extractor.extract_keywords(article_text)
        articleItem['summary'] = summarize(article_text)
        articleItem['link'] = response.url

        yield articleItem
