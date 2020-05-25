import mysql.connector

class NewsScrapingPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="gewurzmuehle30",
            database="newsarticles",
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS testing1""")
        self.curr.execute("""CREATE TABLE testing1(
             headline TEXT,
             data_publish TEXT,
             article_text TEXT,
             )""")

    def store_to_db(self, item):
        self.curr.execute("""INSERT INTO testing1 VALUES (%s, %s, %s)""", (
            item['headline'][0],
            item['date_publish'][0],
            item['article_text'][0]
        ))
        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        return item
