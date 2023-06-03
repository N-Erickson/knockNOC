import os
import requests
import yaml
from flask import Flask, render_template_string
from jinja2 import select_autoescape, Environment, FileSystemLoader
from datetime import datetime, timedelta
import sqlite3
import json
import time
import threading
from collections import deque
from monitoring import ping_history, calculate_uptime, calculate_response_time, check_for_alert

app = Flask(__name__)

# Load configuration from YAML file
config = {}
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Set up Jinja2 template environment
template_loader = FileSystemLoader(searchpath="./templates")
template_env = Environment(loader=template_loader, autoescape=select_autoescape(['html', 'xml']))
template_env.filters['calculate_response_time'] = calculate_response_time

# Register custom filters
template_env.filters['calculate_uptime'] = calculate_uptime

# Load the template
template = template_env.get_template('index.html')

# Ping interval in seconds
ping_interval = config['ping_interval']

# Database initialization logic here

def store_ping_data(endpoint, status, response_time):
    # Store ping data in the database logic here
    pass

@app.route('/')
def home():
    rendered_template = template.render(results=ping_history)
    return rendered_template

if __name__ == '__main__':
    # Start the ping thread
    def send_pings():
        while True:
            for endpoint in config['endpoints']:
                if endpoint not in ping_history:
                    ping_history[endpoint] = deque(maxlen=10)

                try:
                    start_time = datetime.now()
                    response = requests.get(endpoint)
                    response_time = datetime.now() - start_time
                    status = response.ok
                except requests.exceptions.RequestException:
                    response_time = None
                    status = False

                ping_history[endpoint].append((status, response_time))

                # Store the ping data in the database
                store_ping_data(endpoint, status, response_time)

                check_for_alert(endpoint, ping_history[endpoint], config)

            time.sleep(ping_interval)

    ping_thread = threading.Thread(target=send_pings)
    ping_thread.start()

    app.run(debug=True)
