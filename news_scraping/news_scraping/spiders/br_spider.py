# @author: Cristina Bolohan
import scrapy
from ..items import NewsScrapingItem
from scrapy.crawler import CrawlerProcess
import re
from gensim.summarization.summarizer import summarize
import spacy
from string import punctuation
from collections import Counter
from textblob_de import TextBlobDE as TextBlob

class BRSpider(scrapy.Spider):

    name = 'br_spider'
    start_urls = ['https://www.br.de/nachrichten/']
    nlp = spacy.load("de_core_news_lg")

    def parse(self, response):
        nav_bar_url = response.css("#__next > header > div.css-1rumvwz > nav > div > div.css-10gc1wg > div > ul > li > a::attr('href')")

        items = nav_bar_url.extract()

        for page in items:
            exclude = ['newsletter', 'meldungen', 'br24-zeitreise', 'fragbr24']
            next_page = response.urljoin(page)
            if any(key_word in next_page for key_word in exclude):
                continue
            articleItem = NewsScrapingItem()
            articleItem['subject'] = next_page.split('/')[4]
            articleItem['subject'] = articleItem['subject'].split(',')[0]
            request = scrapy.Request(next_page, callback=self.get_all_links)
            request.meta['item'] = articleItem  # By calling .meta, we can pass our item object into the callback.
            yield request

    def get_all_links(self, response):
        articleItem = response.meta['item']
        selector = "article > header > a:nth-child(1)::attr('href')"
        for href in response.css(selector):
            url = response.urljoin(href.extract())
            if "nachrichten" in url:
                request = scrapy.Request(url, callback=self.scrape)
                request.meta['item'] = articleItem
                yield request

    def top_sentences(self, text, limit):
        '''
        :param text: The input text. Can be a short paragraph or a big chuck of text.
        :param limit: The number of sentences to be returned.
        :return: summary of the input text
        '''
        keyword = []
        pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']
        doc = self.nlp(text.lower())
        for token in doc:
            if (token.text in self.nlp.Defaults.stop_words or token.text in punctuation):
                continue
            if (token.pos_ in pos_tag):
                keyword.append(token.text)

        freq_word = Counter(keyword)
        max_freq = Counter(keyword).most_common(1)[0][1]
        for w in freq_word:
            freq_word[w] = (freq_word[w] / max_freq)

        sent_strength = {}
        for sent in doc.sents:
            for word in sent:
                if word.text in freq_word.keys():
                    if sent in sent_strength.keys():
                        sent_strength[sent] += freq_word[word.text]
                    else:
                        sent_strength[sent] = freq_word[word.text]

        summary = []

        sorted_x = sorted(sent_strength.items(), key=lambda kv: kv[1], reverse=True)

        counter = 0
        for i in range(len(sorted_x)):
            summary.append(str(sorted_x[i][0]).capitalize())

            counter += 1
            if (counter >= limit):
                break

        return ' '.join(summary)

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

    def extract_keywords(self, sequence):
        result = []
        nlp = spacy.load("de_core_news_sm")
        # custom list of part of speech tags we are interested in we are interested in proper nouns, nouns, and adjectives
        pos_tag = ['PROPN', 'NOUN']
        # create a spacy doc object by calling the nlp object on the input sequence
        doc = nlp(sequence.lower())
        for chunk in doc.noun_chunks:
            final_chunk = ""
            for token in chunk:
                if (token.pos_ in pos_tag):
                    final_chunk = final_chunk + token.text + " "
            if final_chunk:
                result.append(final_chunk.strip())

        for token in doc:
            if (token.text in self.nlp.Defaults.stop_words or token.text in punctuation):
                continue
            if (token.pos_ in pos_tag):
                result.append(token.text)
        return list(set(result))

    def scrape(self, response):
        articleItem = response.meta['item']
        articleItem['headline'] = response.css('h3::text').extract()
        articleItem['date_publish'] = response.css("time::attr('title')").extract()
        articleItem['article_text'] = response.css('.css-1jftgse p::text').extract()
        article_text = ''.join(articleItem['article_text'])
        articleItem['author'] = response.css(".css-134vnn1 section:nth-child(3) li a span::text").extract()
        articleItem['author'] = ','.join(articleItem['author'])
        txt_blob = TextBlob(article_text)
        articleItem['sentiment'] = txt_blob.sentiment
        key_words = self.get_hotwords(article_text)
        top_key_words = [(kw[0] + ', ') for kw in Counter(key_words).most_common(7)]
        articleItem['keywords'] = ''.join(top_key_words)
        articleItem['summary'] = summarize(article_text, ratio=0.2)
        articleItem['link'] = response.url

        if 'Sekundäre Navigation' in articleItem['headline']: articleItem['headline'].remove('Sekundäre Navigation')

        for i in articleItem['date_publish']:
            pattern = re.compile(r'\d{2}.\d{2}.\d{4}')
            result = re.search(pattern, i)
            articleItem['date_publish'] = result.group()

        yield articleItem

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BRSpider)
    process.start()