import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess

class TagesschauSpider(scrapy.Spider):

    name = 'tagesschau'
    start_urls = ['https://www.tagesschau.de']
    allowed_domains = ['www.tagesschau.de']

    def parse(self, response):
        nav_bar_url = response.css(".ressorts > li > span a::attr('href')")
        items = nav_bar_url.extract()
        for page in items:
            next_page = response.urljoin(page)
            yield scrapy.Request(next_page, callback=self.get_all_links)

    def get_all_links(self, response):
        exclude = ['faktenfinder']
        article_container = "div.teaser > a::attr('href')"
        for href in response.css(article_container):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.scrape)

    def scrape(self, response):
        headline = response.css('.headline::text').extract()
        date_publish = response.css('span.stand::text').extract()
        article_text = response.css('p.text.small::text').extract()
        subject = response.url.split('/')[3]
        link = response.url

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, subject=subject, link=link)
        yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(TagesschauSpider)
    process.start()
