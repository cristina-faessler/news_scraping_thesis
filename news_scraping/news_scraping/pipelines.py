import psycopg2
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class NewsScrapingPipeline(object):

    def __init__(self):
        self.ids_seen = set()

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
        # adapter = ItemAdapter(item)
        # if adapter['link'] in self.ids_seen:
        #     raise DropItem("Duplicate item found: %r" % item)
        # else:
        #     self.ids_seen.add(adapter['link'])
        self.store_to_db(item)
        return item

    def create_table(self):
        drop = """DROP TABLE IF EXISTS news"""
        create_tbl = """CREATE TABLE news (
        article_id serial PRIMARY KEY,
        headline TEXT,
        date_publish TEXT,
        article_text TEXT,
        link TEXT
        )
        """
        self.cur.execute(drop)
        self.cur.execute(create_tbl)
        
    def remove_duplicate(self, item):
        delete_query = """DELETE FROM news T1 using news T2 where t1.ctid < t2.ctid and t1.%s = t2.%s;
                """
        self.cur.execute(delete_query, (item['link'], item['link']))
        self.conn.commit()

    def store_to_db(self, item):

        insert_query = """INSERT INTO news
        (headline, date_publish, article_text, link)
        VALUES (%s, %s, %s, %s)
        """
        self.cur.execute(insert_query, (
            ('').join(item['headline']),
            ('').join(item['date_publish']),
            ('').join(item['article_text']),
            item['link']
        ))
        self.conn.commit()




