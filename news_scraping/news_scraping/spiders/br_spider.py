import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess

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
            yield scrapy.Request(next_page, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = "article > header > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if "nachrichten" in url:
                yield scrapy.Request(url, callback=self.scrape)

    def scrape(self, response):
        headline = response.css('h3::text').extract()
        date_publish = response.css("time::attr('title')").extract()
        date_publish = date_publish[0]
        article_text = response.css('.css-1jftgse p::text').extract()
        subject = response.url.split('/')[4]
        link = response.url

        if 'Sekundäre Navigation' in headline: headline.remove('Sekundäre Navigation')
        # if 'Hinweis:' in article_text[0]: article_text.remove(article_text[0])

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, subject=subject, link=link)

        yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BRSpider)
    process.start()