import sqlite3


class Database:
    def __init__(self, db_name="offers.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_table()

    def __del__(self):
        self.conn.close()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS offers (
                            offerId TEXT PRIMARY KEY,
                            title TEXT,
                            absoluteUri TEXT,
                            isOneClickApply INTEGER
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
        self.conn.close()
