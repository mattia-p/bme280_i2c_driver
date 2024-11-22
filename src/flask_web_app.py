from flask import Flask, render_template
import sqlite3
import plotly.graph_objs as go
import plotly.io as pio
import os

app = Flask(__name__, template_folder='/app/templates')  # If templates are directly inside /app/templates

# Use the RUNFILES_DIR environment variable to get the correct runfiles path
runfiles_dir = os.environ.get('RUNFILES_DIR', '')
if not runfiles_dir:
    # If RUNFILES_DIR is not set, fallback to the default location (adjust based on your setup)
    runfiles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))

DATABASE_PATH = "/app/database/sensor_data.db"

def get_temperature_data():
    """
    Fetch the latest temperature data from the database
    """

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # c.execute("SELECT timestamp, temperature FROM temperature_log")
    c.execute("SELECT timestamp, temperature FROM temperature_log ORDER BY id DESC LIMIT 100")

    data = c.fetchall()
    conn.close()

    timestamps = [row[0] for row in data]
    temperatures = [row[1] for row in data]


    return timestamps, temperatures

@app.route('/')
def index():
    """
    Render the dashboard
    """
    timestamps, temperatures = get_temperature_data()

    # Create a Plotly line graph
    trace = go.Scatter(x=timestamps, y=temperatures, mode='lines', name='Temperature')
    layout = go.Layout(
        title='Temperature Over Time', 
        xaxis={'title': 'Timestamp', 'rangeslider': {'visible': True}},
        yaxis={'title': 'Temperature (°C)'},
    )
    fig = go.Figure(data=[trace], layout=layout)
    
    # Render the plot as HTML
    graph_html = pio.to_html(fig, full_html=False)
    
    # Pass the plot to the template
    return render_template('index.html', plot=graph_html)

if __name__ == "__main__":
    app.run(debug=True)

    