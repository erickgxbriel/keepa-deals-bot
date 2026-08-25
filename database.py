import sqlite3
from typing import Optional
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "deals.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notified_deals (
                    asin TEXT PRIMARY KEY,
                    title TEXT,
                    price REAL,
                    drop_percent REAL,
                    tier TEXT,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP
                )
            """)
            conn.commit()

    def is_already_notified(self, asin: str, current_price: float) -> bool:
        """
        Retorna True se este produto já foi notificado por um preço igual ou menor recentemente.
        Se o preço caiu ainda mais, permite notificar novamente.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price FROM notified_deals WHERE asin = ?", (asin,))
            row = cursor.fetchone()
            if row is None:
                return False
            previous_price = row[0]
            # Se o preço for igual ou maior que a notificação anterior, já notificou
            if current_price >= previous_price:
                return True
            return False

    def save_deal(self, asin: str, title: str, price: float, drop_percent: float, tier: str):
        now = datetime.now()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notified_deals (asin, title, price, drop_percent, tier, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asin) DO UPDATE SET
                    price = excluded.price,
                    drop_percent = excluded.drop_percent,
                    last_seen = excluded.last_seen
            """, (asin, title, price, drop_percent, tier, now, now))
            conn.commit()
