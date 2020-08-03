import scrapy
from ..items import NewsScrapingItem
from summarizer import Summarizer
from transformers import BertModel, BertTokenizer

class RbbSpider(scrapy.Spider):

    name = 'mdr_spider'
    start_urls = ['https://www.mdr.de/nachrichten/index.html']

    def parse(self, response):
        nav = response.css(".level1 > li > a::attr('href')")
        nav_bar = nav.extract()

        for item in nav_bar:
            url = response.urljoin(item)
            if "panorama" in url:
                yield scrapy.Request(url, callback=self.get_all_links)


        nav_menu = response.css(".level1 > li > .level2 > li > a::attr('href')")
        items = nav_menu.extract()
        for page in items:
            exclude = ['podcast', 'chronik']
            next_page = response.urljoin(page)
            if any(key_word in next_page for key_word in exclude):
                continue
            yield scrapy.Request(next_page, callback=self.get_all_links)

    def get_all_links(self, response):
        selector = ".teaser > a::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.scrape)

    def scrape(self, response):
        headline = response.css('h1 > span.headline::text').extract()
        date_publish = response.css('p.webtime > span::text').extract()
        if date_publish is not None:
            date_publish = date_publish[1].replace(',','')
        article_text = response.css('.paragraph > .text::text').extract()
        author =  response.css('p.author::text').extract()
        subject = response.url.split('/')[4]
        link = response.url

        article_text = list(map(lambda x: x.strip(), article_text))
        article_text = ''.join(article_text)
        author = list(map(lambda x: x.strip(), author))

        bertgerman_model = BertModel.from_pretrained('bert-base-german-cased', output_hidden_states=True)
        bertgerman_tokenizer = BertTokenizer.from_pretrained('bert-base-german-cased')
        custom_model = Summarizer(custom_model=bertgerman_model, custom_tokenizer=bertgerman_tokenizer)
        result = custom_model(article_text, min_length=60)
        summary = ''.join(result)

        articleItem = NewsScrapingItem(headline=headline, date_publish=date_publish, article_text=article_text,
                                       author=author, summary=summary, subject=subject, link=link)

        yield articleItem