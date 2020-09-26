import feedparser

def parse(url):
    return feedparser.parse(url)

def get_source(parsed):
    feed = parsed['feed']
    return{
        'link': feed['link'],
        'title': feed['title'],
    }

def get_articles(parsed):
    articles = []
    entries = parsed['entries']
    for entry in entries:
        articles.append({
            'id': entry['id'],
            'title': entry['title'],
            'published': entry['published_parsed'],
            'summary': entry['summary'],
            'link': entry['link'],
        })
    return articles

