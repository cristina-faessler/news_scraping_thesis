## A tool for gathering German news articles and generation of a ready-to-use dataset for NLP tasks

![Scrapy architecture illustration](/Users/cristinabolohan/Downloads/Bachelor Thesis/source/images "Scrapy Architecture Illustraction"){: .shadow}

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

The first requests to perform are specified in the start_urls. The response will
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

### How to run the spider:

In order to extract the news articles from Tagesschau, run the following command: 
**scrapy crawl tagesschau** 



