from flask import Flask, render_template
import sqlite3
import plotly.graph_objs as go
import plotly.io as pio
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

def get_temperature_data():
    """Fetch the latest temperature data from the database"""

    conn = sqlite3.connect('database/sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, temperature FROM temperature_log")

    data = c.fetchall()
    conn.close()

    timestamps = [row[0] for row in data]
    temperatures = [row[1] for row in data]


    return timestamps, temperatures

@app.route('/')
def index():
    """Render the dashboard"""
    timestamps, temperatures = get_temperature_data()

    # Create a Plotly line graph
    trace = go.Scatter(x=timestamps, y=temperatures, mode='lines', name='Temperature')
    layout = go.Layout(title='Temperature Over Time', xaxis={'title': 'Timestamp'}, yaxis={'title': 'Temperature (°C)'})
    fig = go.Figure(data=[trace], layout=layout)
    
    # Render the plot as HTML
    graph_html = pio.to_html(fig, full_html=False)
    
    # Pass the plot to the template
    return render_template('index.html', plot=graph_html)

if __name__ == "__main__":
    app.run(debug=True)

    