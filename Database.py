import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self, db_name="job_offers"):
        self.db_name = db_name
        self.conn = self.connect_to_db()
        self.cur = self.conn.cursor()
        self.create_table()

    def __del__(self):
        self.close_connection()

    @staticmethod
    def connect_to_db():
        try:
            connection_string = os.getenv('DATABASE_URL')
            return psycopg2.connect(connection_string)
        except psycopg2.OperationalError as e:
            print(f'Error with connecting to database: {e}')
            raise

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS offers (
                            offerId TEXT PRIMARY KEY,
                            title TEXT,
                            absoluteUri TEXT,
                            isOneClickApply BOOLEAN
                            )''')
        self.conn.commit()

    def offer_exists(self, offer_id):
        self.cur.execute("SELECT * FROM offers WHERE offerId=?", (offer_id,))
        offer = self.cur.fetchone()
        return offer is not None

    def insert_offer(self, offer_id, title, absolute_uri, is_one_click_apply):
        self.cur.execute("INSERT INTO offers VALUES (?, ?, ?, ?)",
                         (offer_id, title, absolute_uri, is_one_click_apply))
        self.conn.commit()

    def offer_exists_from_json(self, offer_json):
        offer_id = offer_json['offers'][0]['partitionId']
        return self.offer_exists(offer_id)

    def save_offer_from_json(self, offer_json):
        offer_id = offer_json['offers'][0]['partitionId']
        title = offer_json['jobTitle']
        absolute_uri = offer_json['offers'][0]['offerAbsoluteUri']
        is_one_click_apply = offer_json['isOneClickApply']

        print(offer_id, title, absolute_uri, is_one_click_apply)
        self.insert_offer(offer_id, title, absolute_uri, is_one_click_apply)

    def get_all(self):
        self.cur.execute("SELECT * FROM offers")
        return self.cur.fetchall()

    def get_offer_by_id(self, offer_id):
        self.cur.execute("SELECT * FROM offers WHERE offerId=?", (offer_id,))
        row = self.cur.fetchone()
        if row:
            return {
                "offerId": row[0],
                "title": row[1],
                "absoluteUri": row[2],
                "isOneClickApply": row[3]
            }
        return None

    def close_connection(self):
        if self.conn:
            self.conn.close()
        if self.cur:
            self.cur.close()

    def test_connection(self):
        self.cur.execute("SELECT NOW()")
        time = self.cur.fetchone()[0]
        self.cur.execute("SELECT version()")
        version = self.cur.fetchone()[0]
        print(time, version)


if __name__ == '__main__':
    db = Database()
    db.test_connection()
