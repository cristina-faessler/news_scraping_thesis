import scrapy
import os
from ..items import NewsScrapingItem
from bs4 import BeautifulSoup
import json
import unidecode as ud
import requests
from scrapy.crawler import CrawlerProcess

class NewsSpider(scrapy.Spider):

    name = 'news'

    def __init__(self, *args, **kwargs):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, "base_urls.txt")
        with open(abs_file_path) as f:
            self.start_urls = [url.strip() for url in f.readlines()]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.find_urls)

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

        tag = params['url_params'][value]['tag']
        keyword = params['url_params'][value]['keyword']
        exclude = params['url_params'][value]['exclude']

        return tag, keyword, exclude

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

    def find_urls(self, response):

        urls = []

        url_params = NewsSpider.open_url_params(self)
        for param in range(len(url_params['url_params'])):
            tag, keyword, exclude = NewsSpider.get_url_params(self, url_params, param)

            soup = BeautifulSoup(response.body, 'html.parser')
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
                            urls.append(response.urljoin(link))
                    except TypeError:
                        print('Error retrieving anchor tags')
            urls = list(set(urls))
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)

    def clean_news_article(self, headline, date_publish, article_text):
        """Removes \n from text"""
        headline = list(map(lambda x: x.strip(), headline))
        date_publish = list(map(lambda x: x.strip(), date_publish))
        article_text = list(map(lambda x: x.strip(), article_text))

        return headline, date_publish, article_text

    def parse(self, response):

        article_params = NewsSpider.open_article_params(self)
        for param in range(len(article_params['article_params'])):
            headline, date_publish, article_text = NewsSpider.get_article_params(self, article_params, param)

            headline = response.css(headline).extract()
            date_publish = response.css(date_publish).extract()
            article_text = response.css(article_text).extract()
            link = response.url

            NewsSpider.clean_news_article(self, headline, article_text, date_publish)

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           link=link)

            yield articleItem




# run Scrapy from Script
# process = CrawlerProcess()
# process.crawl(NewsSpider)
# process.start()



