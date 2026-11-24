
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone


DB_PATH = os.getenv("DB_PATH", "data/heart_rates.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

    with closing(get_connection()) as connection:
        connection.execute("""
                           CREATE TABLE IF NOT EXISTS heart_rate_data (
                                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                          device_id TEXT NOT NULL,
                                                                          heart_rate INTEGER NOT NULL,
                                                                          timestamp DATETIME NOT NULL
                           )
                           """)

        connection.commit()

    print("Database initialized successfully")


def insert_reading(device_id, heart_rate):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with closing(get_connection()) as connection:
        connection.execute("""
                           INSERT INTO heart_rate_data
                               (device_id, heart_rate, timestamp)
                           VALUES (?, ?, ?)
                           """, (device_id, heart_rate, timestamp))

        connection.commit()


def get_readings(device_id=None):
    with closing(get_connection()) as connection:
        if device_id:
            readings = connection.execute("""
                                          SELECT device_id, heart_rate, timestamp
                                          FROM heart_rate_data
                                          WHERE device_id = ? COLLATE NOCASE
                                          ORDER BY timestamp DESC, id DESC
                                          """, (device_id,)).fetchall()

        else:
            readings = connection.execute("""
                                          SELECT device_id, heart_rate, timestamp
                                          FROM heart_rate_data
                                          ORDER BY timestamp DESC, id DESC
                                          """).fetchall()

    return readings
