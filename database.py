import sqlite3
import json

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS miners (
                hotkey TEXT PRIMARY KEY,
                performance REAL,
                last_submission INTEGER
            )
        ''')
        self.conn.commit()

    def register_miner(self, hotkey):
        self.cursor.execute('INSERT OR IGNORE INTO miners (hotkey, performance, last_submission) VALUES (?, ?, ?)', 
                            (hotkey, 0, 0))
        self.conn.commit()

    def update_miner_performance(self, hotkey, performance, timestamp):
        self.cursor.execute('UPDATE miners SET performance = ?, last_submission = ? WHERE hotkey = ?', 
                            (performance, timestamp, hotkey))
        self.conn.commit()

    def get_miner_performances(self):
        self.cursor.execute('SELECT hotkey, performance FROM miners')
        return dict(self.cursor.fetchall())

    def close(self):
        self.conn.close()