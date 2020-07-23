import scrapy
from ..items import NewsScrapingItem

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
        articleItem['link'] = response.url

        # articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, subject=subject, link=link)
        yield articleItem
