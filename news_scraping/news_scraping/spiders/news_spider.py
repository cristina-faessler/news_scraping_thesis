import scrapy
import os
from ..items import NewsScrapingItem
import json
import requests
import unidecode as ud
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.loader import ItemLoader

class NewsScraper(scrapy.Spider):

    name = 'scraper'

    def start_requests(self):
        url_params = NewsScraper.open_url_params(self)
        for param in range(len(url_params['url_params'])):
            base_url, tag, keyword, exclude = NewsScraper.get_url_params(self, url_params, param)
            urls = self.find_urls(base_url, tag, keyword, exclude)
            self.start_urls = urls.copy()
            for url in self.start_urls:
                print(url)
                item = NewsScrapingItem()
                item['link'] = url
                request = scrapy.Request(url)
                request.meta['item'] = item
                yield request

    def open_article_params(self):
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir,'parse.json'), 'r') as myfile:
            data = myfile.read()
        obj = json.loads(data)
        return obj

    def open_url_params(self):
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir,'find_urls.json'), 'r') as myfile:
            data = myfile.read()
        obj = json.loads(data)
        return obj

    def get_article_params(self, params, value):

        headline = params['article_params'][value]['headline']
        date_publish = params['article_params'][value]['date_publish']
        article_text = params['article_params'][value]['article_text']

        return headline, date_publish, article_text

    def get_url_params(self, params, value):

        base_url = params['url_params'][value]['base_url']
        tag = params['url_params'][value]['tag']
        keyword = params['url_params'][value]['keyword']
        exclude = params['url_params'][value]['exclude']

        return base_url, tag, keyword, exclude

    def clean_link(self, link, keyword, exclude):
        if keyword is not None:
            keyword = keyword.split(',')
            if any(key_word in link for key_word in keyword) == False:
                return False

            if exclude is not None:
                exclude = exclude.split(',')
                if any(key_word in link for key_word in exclude) == True:
                    return False

            return True

    def clean_news_article(self, headline, date_publish, article_text):
        """Removes \n from text"""
        for str in article_text:
            str.replace("|", " ")
        headline = list(map(lambda x: x.strip(), headline))
        date_publish = list(map(lambda x: x.strip(), date_publish))
        article_text = list(map(lambda x: x.strip(), article_text))

        return headline, date_publish, article_text

    def find_urls(self, base_url, tag, keyword, exclude):
        urls = []
        r = requests.get(base_url)
        soup = BeautifulSoup(r.text, 'html.parser')

        article_tag = soup.find_all(tag)
        for tag in article_tag:
            for a in tag.find_all('a'):
                try:
                    link = a.get('href')

                    if not self.clean_link(link, keyword, exclude):
                        continue

                    link = ud.unidecode(link)
                    if "http" in link:
                        urls.append(link)
                    else:
                        urls.append(os.path.join('https://', (base_url.split('/')[2]), link.strip('/')))
                except TypeError:
                    print('Error retrieving anchor tags')
        urls = list(set(urls))
        return urls

    # def parse(self, response):
    #
    #     article_params = NewsScraper.open_article_params(self)
    #     for param in range(len(article_params['article_params'])):
    #         headline, date_publish, article_text = NewsScraper.get_article_params(self, article_params, param)
    #
    #     item = response.meta['item']
    #     print(item)

        # for item in self.parse_article(response):
        #     yield item
        #     item['headline'] = response.css(headline).extract()
        #     item['date_publish'] = response.css(date_publish).extract()
        #     item['article_text'] = response.css(article_text).extract()
        #     # item['link'] = response.request.url
        #     yield item

        # item = NewsScrapingItem()
        # item['link'] = response.request.url
        #
        # request = scrapy.Request(url=response.request.url)
        # request.meta['item'] = item  # By calling .meta, we can pass our item object into the callback.
        # yield request

    def parse(self, response):
        # headline = []
        # date_publish = []
        # article_text = []

        article_params = NewsScraper.open_article_params(self)
        for param in range(len(article_params['article_params'])):
            headline, date_publish, article_text = NewsScraper.get_article_params(self, article_params, param)
            print(headline, date_publish, article_text)

            item = response.meta['item']
            item['headline'] = response.css(str(headline)).extract()
            item['date_publish'] = response.css(date_publish).extract()
            item['article_text'] = response.css(article_text).extract()

            yield item.copy()
# run Scrapy from Script
# process = CrawlerProcess()
# process.crawl(NewsSpider)
# process.start()



