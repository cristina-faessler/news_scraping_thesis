#extracted Data - Temporary containers (items) - storing in database
import scrapy
import os
from ..items import NewsScrapingItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from bs4 import BeautifulSoup
import json
from scrapy.crawler import CrawlerProcess

class NewsSpider(scrapy.Spider):

    name = 'news'

    """This spider has one rule: extract all (unique and canonicalized) links,
     follow them and parse them using the parse_items method"""
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback='parse'
        )
    ]

    def __init__(self, *args, **kwargs):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, "website_urls.txt")
        with open(abs_file_path) as f:
            self.start_urls = [url.strip() for url in f.readlines()]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.find_urls)

    def open_var_tags(self):
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir,'variable_tags.json'), 'r') as myfile:
            data = myfile.read()
        obj = json.loads(data)
        return obj

    def get_params(self, var_tags, tag):
        headline = var_tags['var_tags'][tag]['headline']
        date_publish = var_tags['var_tags'][tag]['date_publish']
        article_text = var_tags['var_tags'][tag]['article_text']

        return headline, date_publish, article_text

    def find_urls(self, response):
        """Only extract canonicalized and unique links (with respect to the current page)"""
        # links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        soup = BeautifulSoup(response.body, 'html.parser')
        # for link in links:
        #     print(link.url)
        for a in soup.find_all('a'):
            if a.get('href') is not None:
                url = response.urljoin(a.get('href'))
                yield scrapy.Request(url, callback=self.parse)


    #parse function
    def parse(self, response):
        var_tags = NewsSpider.open_var_tags(self)
        for tag in range(len(var_tags['var_tags'])):
            headline, date_publish, article_text = NewsSpider.get_params(self, var_tags, tag)

            headline = response.css(headline).extract()
            date_publish = response.css(date_publish).extract()
            article_text = response.css(article_text).extract()
            link = response.url

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text, link=link)
            return articleItem

# run Scrapy
process = CrawlerProcess()
process.crawl(NewsSpider)
process.start()



