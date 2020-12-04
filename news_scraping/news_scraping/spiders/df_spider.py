# @author: Cristina Bolohan
import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess
from gensim.summarization.summarizer import summarize
import spacy
from string import punctuation
from collections import Counter
from textblob_de import TextBlobDE as TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.corpus import stopwords

class DFSpider(scrapy.Spider):

    name = 'df_spider'
    start_urls = ['https://www.deutschlandfunk.de/die-nachrichten.1441.de.html']
    allowed_domains = ['deutschlandfunk.de']
    nlp = spacy.load("de_core_news_lg")

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

    def get_hotwords(self, text):
        result = []
        pos_tag = ['PROPN', 'NOUN']
        doc = self.nlp(text.lower())
        for token in doc:
            if (token.text in self.nlp.Defaults.stop_words or token.text in punctuation):
                continue
            if (token.pos_ in pos_tag):
                result.append(token.text)
        return result

    def sentiment(self, text):
        pos_count = 0
        pos_correct = 0
        neg_count = 0
        neg_correct = 0

        for line in text.split('.'):
            analysis = TextBlob(line)
            if analysis.sentiment.polarity > 0:
                pos_correct += 1
            pos_count += 1
            if analysis.sentiment.polarity <= 0:
                neg_correct += 1
            neg_count += 1
        return "Positive accuracy = {:0.2f}%".format(pos_correct/pos_count * 100.0) + \
               " Negative accuracy = {:0.2f}%".format(neg_correct/neg_count * 100.0)

    def remove_stop_words(self, text):
        result = []
        nlp = spacy.load("de_core_news_lg")
        doc = nlp(text.lower())

        for token in doc:
            if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
                continue
            else:
                result.append(token.text)
        return result

    def topic_modelling(self, article):
        topic_dict = {0: '', 1: '', 2:''}
        tfidf = TfidfVectorizer(max_df=0.95, min_df=2)
        dtm = tfidf.fit_transform(article)
        nmf_model = NMF(n_components=3)
        nmf_model.fit(dtm)

        for index, topic in enumerate(nmf_model.components_):
            print(f'The top 15 words for topic # {index}')
            print([tfidf.get_feature_names()[i] for i in topic.argsort()[-15:]])

        topic_results = nmf_model.transform(dtm)
        return topic_results
        # text['Topic'] = topic_results.argmax(axis=1)
        # text['Topic label'] = text['Topic'].map(topic_dict)

    def scrape(self, response):

        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h1::text').extract()
        articleItem['date_publish'] = response.css('time::text').extract()
        articleItem['article_text'] = response.css('.articlemain > p::text').extract()
        article_text = ''.join(articleItem['article_text'])

        articleItem['sentiment'] = self.sentiment(article_text)

        clean_txt = self.remove_stop_words(article_text)
        topics = self.topic_modelling(clean_txt)

        hot_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(hot_words).most_common(7)]
        articleItem['keywords'] = ''.join(top_key_words)

        articleItem['summary'] = summarize(article_text, ratio=0.2)
        articleItem['author'] = ''
        articleItem['link'] = response.url

        while '\n' in articleItem['headline']: articleItem['headline'].remove('\n')

        print(topics)
        # yield articleItem


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(DFSpider)
    process.start()


