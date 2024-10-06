from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_temperature_data():
    """Fetch the latest temperature data from the database"""

    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, temperature FROM temperature_log ORDER BY id DESC LIMIT 10")

    data = c.fetchall()
    conn.close()

    return data

@app.route('/')
def index():
    """Render the dashboard"""

    temperature_data = get_temperature_data()
    return render_template('index.html', temperature_data=temperature_data)

if __name__ == "__main__":
    app.run(debug=True)

    