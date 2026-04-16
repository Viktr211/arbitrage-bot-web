# database.py
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "user_data.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                wallet_address TEXT,
                balance REAL DEFAULT 10000.0,
                total_profit REAL DEFAULT 0.0,
                trade_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'approved',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset TEXT,
                profit REAL,
                buy_exchange TEXT,
                sell_exchange TEXT,
                trade_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

def create_user(email, password, full_name, wallet_address):
    with get_db() as conn:
        conn.execute('''
            INSERT OR IGNORE INTO users (email, password, full_name, wallet_address)
            VALUES (?, ?, ?, ?)
        ''', (email, password, full_name, wallet_address))

def get_user(email):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def add_trade(user_id, asset, profit, buy_ex, sell_ex):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO trades (user_id, asset, profit, buy_exchange, sell_exchange)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, asset, profit, buy_ex, sell_ex))
        conn.execute('''
            UPDATE users SET total_profit = total_profit + ?, trade_count = trade_count + 1
            WHERE id = ?
        ''', (profit, user_id))
