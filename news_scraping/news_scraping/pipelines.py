import psycopg2

class NewsScrapingPipeline(object):

    def open_spider(self, spider):
        host = 'localhost'
        usr = 'postgres'
        pwd = 'dbs2'
        db = 'postgres'
        self.conn = psycopg2.connect(host=host, user=usr, password=pwd, dbname=db)
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        self.store_to_db(item)
        return item

    def store_to_db(self, item):
        self.cur.execute("""INSERT INTO news (headline, date_publish, article_text) VALUES (%s, %s, %s)""",(
            item['headline'],
            item['date_publish'],
            item['article_text'],
        ))
        self.conn.commit()

