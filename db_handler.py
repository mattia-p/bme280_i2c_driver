import sqlite3
import time

def init_db():
    """Initializes the SQLite database and creates the table"""

    conn = sqlite3.connect('sensor_data.db')

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

    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

    c.execute("INSERT INTO temperature_log (timestamp, temperature) VALUES (?, ?)", 
              (timestamp, temperature))
    conn.commit()
    conn.close()