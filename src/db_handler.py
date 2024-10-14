import sqlite3
import time
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../database/sensor_data.db')

def init_db():
    """Initializes the SQLite database and creates the table"""

    conn = sqlite3.connect(DATABASE_PATH)

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS temperature_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    temperature REAL
                )''')
    conn.commit()
    conn.close()

def save_temperature_to_db(temperature):
    """Inserts temperature data into the SQLite database"""

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

    c.execute("INSERT INTO temperature_log (timestamp, temperature) VALUES (?, ?)", 
              (timestamp, temperature))
    conn.commit()
    conn.close()