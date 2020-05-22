# import mysql.connector
import sqlite3

class NewsScrapingPipeline(object):

    # def __init__(self):
    #     self.create_connection()
    #     self.create_tb()
    #
    # def create_connection(self):
    #     self.conn = sqlite3.connect('news.db')
    #     self.curr = self.conn.cursor()
    #
    # def create_tb(self):
    #     self.curr.execute("""DROP TABLE IF EXISTS news_tb""")
    #     self.curr.execute("""create table news_tb (
    #                     dachzeile text,
    #                     headline text,
    #                     teaser_text text,
    #                     links text
    #                     )""")


    # def __init__(self):
    #     self.create_connection()
    #     self.create_table()
    #
    # def create_connection(self):
    #     self.conn = mysql.connector.connect(
    #         host = 'localhost',
    #         user = 'root',
    #         passwd = 'gewurzmuehle30',
    #         database = 'news_db',
    #     )
    #     self.curr = self.conn.cursor()

    # def create_table(self):
    #     self.curr.execute("""DROP TABLE IF EXISTS testing_tb""")
    #     self.curr.execute("""CREATE TABLE testing_tb(
    #          dachzeile text,
    #          headline text,
    #          teaser_text text,
    #          links text,
    #          )""")

    def process_item(self, item, spider):
        # self.store_db(item)
        # self.store_to_db(item)
        return item


    # def store_db(self, item):
    #     self.curr.execute("""insert into news_tb values(?,?,?,?)""",(
    #         item['dachzeile'],
    #         item['headline'],
    #         item['teaser_text'],
    #         item['links']
    #     ))
    #     self.conn.commit()

    # def store_to_db(self, item):
    #     self.curr.execute("""INSERT INTO testing_tb VALUES (%s, %s, %s, %s)""", (
    #         item['dachzeile'][0],
    #         item['headline'][0],
    #         item['teaser_text'][0],
    #         item['links'][0]
    #     ))
    #     self.conn.commit()
