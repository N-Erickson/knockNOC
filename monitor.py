import os
import requests
import yaml
from flask import Flask, render_template_string
from jinja2 import select_autoescape, Environment, FileSystemLoader
from collections import deque
from datetime import datetime, timedelta
import sqlite3
import threading
import time

app = Flask(__name__)

# Set up SQLite database
database_path = 'ping_history.db'

if not os.path.exists(database_path):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE pings
                 (endpoint TEXT, status INTEGER, response_time FLOAT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# Load configuration from config.yaml
with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file)

# Get the ping_interval value from the config
ping_interval = config.get('ping_interval', 5)  # Default to 5 seconds if not specified in config


ping_history = {}
#ping_interval = 5  # Interval in seconds for pinging the endpoints


def calculate_uptime(pings):
    if not pings:
        return 0

    successful_pings = sum(status for status, _ in pings)
    uptime_percentage = (successful_pings / len(pings)) * 100
    return round(uptime_percentage, 2)


def calculate_response_time(pings):
    if not pings:
        return None

    total_response_time = sum(response_time.total_seconds() for _, response_time in pings if response_time)
    average_response_time = total_response_time / len(pings)
    return round(average_response_time, 2)


env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)
env.filters['calculate_uptime'] = calculate_uptime
env.filters['calculate_response_time'] = calculate_response_time


def perform_ping(endpoint):
    try:
        start_time = datetime.now()
        response = requests.get(endpoint)
        response_time = datetime.now() - start_time
        status = response.ok
    except requests.exceptions.RequestException:
        response_time = None
        status = False

    if endpoint not in ping_history:
        ping_history[endpoint] = deque(maxlen=10)

    ping_history[endpoint].append((status, response_time))

    # Store the ping data in the database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("INSERT INTO pings VALUES (?, ?, ?, ?)",
              (endpoint, int(status), response_time.total_seconds() if response_time else None, str(datetime.now())))
    conn.commit()
    conn.close()


def ping_endpoints():
    while True:
        with open('config.yaml') as config_file:
            config = yaml.safe_load(config_file)

        for endpoint in config['endpoints']:
            perform_ping(endpoint)

        # Sleep for the specified interval before pinging again
        time.sleep(ping_interval)


@app.route('/')
def home():
    template = env.get_template('index.html')
    rendered_template = template.render(results=ping_history)

    return render_template_string(rendered_template)


if __name__ == '__main__':
    # Start the background thread for pinging endpoints
    threading.Thread(target=ping_endpoints, daemon=True).start()

    app.run(debug=True)
