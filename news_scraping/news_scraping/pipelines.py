import psycopg2
from psycopg2 import sql

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
        # self.remove_duplicates(item)
        return item

    def create_table(self):
        self.cur.execute("""DROP TABLE IF EXISTS news""")
        self.cur.execute("""CREATE TABLE news (
        article_id serial PRIMARY KEY,
        headline TEXT,
        date_publish TEXT,
        article_text TEXT,
        link TEXT
        )
        """)

    def remove_duplicates(self, item):
        pass
        # delete_query = sql.SQL("delete from {} T1 using {} T2 where T1.ctid < T2.ctid and T1.{} = T2.{};").format(
        #     sql.Identifier("news"),
        #     sql.Identifier("news"),
        #     sql.Placeholder(),
        #     sql.Placeholder()
        # )
        # print(delete_query.as_string(self.conn))
        # self.cur.execute(delete_query, ['link'], ['link'])
        # self.conn.commit()
        # select_query = sql.SQL("SELECT DISTINCT {} from {}").format(
        #     sql.Identifier(item['link']),
        #     sql.Identifier("news")
        # )
        # print(select_query.as_string(self.conn))
        # self.cur.execute(select_query)
        #
        # row_count = self.cur.rowcount
        # print(row_count, "Record Deleted")


    def store_to_db(self, item):
        # field_lst = [fld_name for fld_name in item.keys()]
        # insert_query = sql.SQL("INSERT INTO news ({}) VALUES ({})").format(
        #     sql.SQL(',').join(map(sql.Identifier, field_lst)),
        #     sql.SQL(',').join(map(sql.Placeholder, field_lst))
        # )
        # print(insert_query.as_string(self.conn))
        # self.cur.execute(insert_query)
        # self.conn.commit()

        # query = """INSERT INTO news (headline, date_publish, article_text, link)
        # SELECT '{}', '{}, '{}', '{}'
        # WHERE NOT EXISTS (SELECT link from news WHERE link = link);
        # """.format(item['headline'], item['date_publish'], item['article_text'], item['link'])
        # self.cur.execute(query)
        # self.conn.commit()

        insert_query = """INSERT INTO news (headline, date_publish, article_text, link)
        VALUES (%s, %s, %s, %s)"""

        self.cur.execute(insert_query, (
            ('').join(item['headline']),
            ('').join(item['date_publish']),
            ('').join(item['article_text']),
            ('').join(item['link'])
        ))
        self.conn.commit()

