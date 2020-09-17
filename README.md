## A Tool for Gathering German News Articles and Generation of a ready-to-use Data Set for NLP Tasks

![Scrapy architecture illustration](/news_scraping/news_scraping/source/images/tool_doc_illustration.jpg "Scrapy Architecture Illustration")

### Requirements
- Scrapy
- SpaCy 
- gensim
- de_core_news_lg
- psycopg2

A tool for gathering German news articles and storage into PostgreSQL.
The continuous extraction of news allows the extension of the database and the 
availability of a large dataset, which can further be used for certain NLP tasks. 

For the extraction of structured data like headline, date, article text, topic, 
authors, we have used a free and open-source scraping and web-crawling framework 
written in Python, which name is Scrapy. 

In order to collect the data, for each news portal has been created a spider. 
Spiders are classes which define how a certain site will be scraped, including 
how to perform the crawl and how to extract structured data from their pages. 
In other words, Spiders are the place where you define the custom behaviour for 
crawling and parsing pages for a particular site. 

The three requirements a spider should have are:
- a name: identifies the Spider. It must be unique within a project, that is, you can’t set the same name for different Spiders.
- a start url: first requests to perform
- a parse() function: The parse() method will be called to handle each of the requests
for those URLs, even though we haven’t explicitly told Scrapy to do so. This happens because parse()
is Scrapy’s default callback method, which is called for requests without an explicitly assigned callback.

Scrapy uses **Request** and **Response** objects for crawling web sites. Typically, 
**Request** objects are generated in the spiders and pass across the system until
they reach the Downloader, which executes the request and returns a **Response** object 
which travels back to the spider that issued the request.

### Web Crawler

The first requests to perform are specified in the `start_urls`. The response will
be received in the parse function. 

**parse():** looks for all the links in the navigation bar of the website

**get_all_links():** as the name already suggests, the method is getting all the links from each section of the navigation bar 

### Web Scraper

**scrape():** is extracting the data we want to generate a dataset from

The data is structured and stored as _items_, Python objects that define key-value pairs. Each object contains the following set of values:

- headline 
- date published
- article text 
- authors 
- keywords 
- summary 
- subject
- link 

### Item Pipeline

After an item has been scraped by a spider, it is sent to the Item Pipeline which processes it through several components that are executed sequentially.
Each item pipeline component is a Python class that must implement the following method:

`process_item(self, item, spider)` 
This method is called for every item pipeline component.

**process_item()** must either: return an *item* object, return a **Deferred** or raise a **DropItem** exception.
> **Parameters**
- **item** - the scraped item
- **spider** - the spider which scraped the item

**store_to_db(self, item):** stores the scraped item in a `PostgreSQL` database

### NLP Tasks

For keywords extraction we used the German language model provided by spaCy, an open-source software library for advanced Natural Language Processing. 

`get_hotwords(self, text):` this method is taking as input parameters the news article text and is extracting the keywords using the part of speech tagging. 
It is tagging the `PROPN` (proper noun) and `NOUN` (noun) for now. If you would like to extract another part of speech tag such as a verb, extend the list
based on your requirements. Afterwards it is converting the input text into lowercase and tokenizing it via the spaCy model that we have loaded using `nlp = spacy.load("de_core_news_lg")`. 
A processed `Doc` object will be returned. The object contains `Token` objects based on the tokenization process. It loops then over each token and determine if the tokenized text is part 
of the default stopwords or punctuation. It stores the result if the part of speech tag of the tokenized text is the one that we have specified previously. And finally it returns the result as a list of strings.

We use the `Counter` module to sort and get the most frequent keywords by retaining the frequency of each word. The `Counter` module has a `most_common` function that accepts an integer as 
an input parameter. 

`summarize(self, article_text, ratio):` is getting a summarized version of the given article text with the help of `gensim.summarizer` module. Summarizing is based on ranks of text sentences using a variation of the TextRank algorithm.
> **Parameters**
- article_text (str) – Given text.
- ratio (float, optional) – Number between 0 and 1 that determines the proportion of the number of sentences of the original text to be chosen for the summary.

### Scheduling Jobs With Crontab on macOS

Running scripts on your computer is great. Running them automatically is even better! Automatic running on MacOS (and Linux) can be done by setting cron jobs. 

Setting cron jobs requires a specific format.

```
* * * * * command
* - minute (0-59)
* - hour (0-23)
* - day of the month (1-31)
* - month (1-12)
* - day of the week (0-6, 0 is Sunday)
command - command to execute
(from left-to-right)
```

For all existing spiders, cron jobs for automatic web scraping have been set. 

![Cron Jobs](/news_scraping/news_scraping/source/images/crontab_jobs.png "Cron Jobs")

For example, the new published news articles from BR will be collected daily at 9:15, 12:15 and 17:15 o'clock. 

### How to Run the Spider:

In order to extract the news articles from Tagesschau, run the following command: 
**scrapy crawl tagesschau** 

For collecting the news from another news portal, change the `name` of the *spider* in the following command: **scrapy crawl name**



