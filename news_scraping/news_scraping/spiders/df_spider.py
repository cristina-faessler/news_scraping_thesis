import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess

class DFSpider(scrapy.Spider):

    name = 'df_spider'
    start_urls = ['https://www.deutschlandfunk.de/die-nachrichten.1441.de.html']
    allowed_domains = ['deutschlandfunk.de']

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

    def scrape(self, response):
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h1::text').extract()
        articleItem['date_publish'] = response.css('time::text').extract()
        articleItem['article_text'] = response.css('.articlemain > p::text').extract()
        articleItem['link'] = response.url

        while '\n' in articleItem['headline']: articleItem['headline'].remove('\n')

        yield articleItem


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(DFSpider)
    process.start()


