#extracted Data - Temporary containers (items) - storing in database
import scrapy
from ..items import NewsScrapingItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from bs4 import BeautifulSoup

class TagesschauSpider(scrapy.Spider):

    name = 'news'
    start_urls = ['https://www.tagesschau.de/']
    # with open("../websites_url.txt", "r") as file:
    #      start_urls = [url.strip() for url in file.readlines()]
    #This spider has one rule: extract all (unique and canonicalized) links, follow them and parse them using the parse_items method
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback='parse_news_article'
        )
    ]

    def start_requests(self):
        """Method which starts the requests by visiting all URLs specified in start_urls"""
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    #parse function
    def parse(self, response):
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        soup = BeautifulSoup(response.body, 'html.parser')
        # for link in links:
        #     print(link.url)
        for a in soup.find_all('a'):
            if a.get('href') is not None:
                url = response.urljoin(a.get('href'))
                yield scrapy.Request(url, callback=self.parse_news_article)

        # anchor_selector = "div.teaser > a::attr('href')"
        # for href in response.css(anchor_selector):
        #     url = response.urljoin(href.extract())
        #     yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):

            headline = response.css('.headline::text').extract()
            date_publish = response.css('span.stand::text').extract()
            article_text = response.css('p.text.small::text').extract()
            link = response.url

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)

            return articleItem