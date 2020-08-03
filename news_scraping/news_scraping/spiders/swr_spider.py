import scrapy
from ..items import NewsScrapingItem
import yake
from gensim.summarization.summarizer import summarize
class RbbSpider(scrapy.Spider):

    name = 'swr_spider'
    start_urls = ['https://www.swr.de/swraktuell/swraktuell-100.html']

    def parse(self, response):
        nav_bar = response.css(".navbar-nav > li > a::attr('href')").extract()

        for item in nav_bar:
            url = response.urljoin(item)
            if "swraktuell" in url:
                yield scrapy.Request(url, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = "h2 > a::attr('href')"
        exclude = ['radio', 'wahl', 'newsletter', 'sendung', 'video', 'rueckschau']
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if any(key_word in url for key_word in exclude):
                continue
            yield scrapy.Request(url, callback=self.parse_news_article)

    def parse_news_article(self, response):
        if "swraktuell" in response.url:
            headline = response.css("div > header > h1 > span[itemprop='headline']::text").extract()
            date_publish = response.css('time > .date::text').extract()
            if date_publish is not None:
                date_publish = date_publish[0]
            article_text = response.css('.bodytext p::text').extract()
            article_text = ''.join(article_text)
            subject = response.url.split('/')[4]
            author = response.css('footer > div > dl.meta-authors > dd::text').extract()
            author = list(map(lambda x: x.strip(), author))
            kw_extractor = yake.KeywordExtractor(lan='de', top=10)
            keywords = kw_extractor.extract_keywords(article_text)
            summary = summarize(article_text)
            link = response.url

            articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                           subject=subject, author=author, keywords=keywords, summary=summary, link=link)

            yield articleItem