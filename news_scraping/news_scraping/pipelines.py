import psycopg2

class NewsScrapingPipeline(object):

    def open_spider(self, spider):
        host = 'localhost'
        usr = 'postgres'
        pwd = 'dbs2'
        db = 'postgres'
        self.conn = psycopg2.connect(host=host, user=usr, password=pwd, dbname=db)
        self.cur = self.conn.cursor()
        self.create_table()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        self.store_to_db(item)
        return item

    def create_table(self):
        drop = """DROP TABLE IF EXISTS news"""
        create_tbl = """CREATE TABLE news (
        article_id serial PRIMARY KEY,
        headline TEXT,
        date_publish TEXT,
        article_text TEXT,
        authors TEXT,
        keywords TEXT,
        summary TEXT,
        subject TEXT,
        link TEXT
        )
        """
        self.cur.execute(drop)
        self.cur.execute(create_tbl)

    def store_to_db(self, item):

        insert_query = """INSERT INTO news
        (headline, date_publish, article_text, authors, keywords, summary, subject, link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cur.execute(insert_query, (
            ('').join(item['headline']),
            ('').join(item['date_publish']),
            ('').join(item['article_text']),
            ('').join(item['author']),
            item['keywords'],
            item['summary'],
            item['subject'],
            item['link']
        ))
        self.conn.commit()




