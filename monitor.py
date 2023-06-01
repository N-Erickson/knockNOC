import os
import requests
import yaml
from flask import Flask, render_template_string
from jinja2 import select_autoescape, Environment, FileSystemLoader
from collections import deque
from datetime import datetime, timedelta
import sqlite3
import json
import time
import threading

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

ping_history = {}
last_alert_timestamps = {}
ping_interval = 1  # Default ping interval in seconds

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

def send_pagerduty_alert(endpoint, api_key):
    payload = {
        "event_action": "trigger",
        "client": "Uptime Monitor",
        "client_url": "",
        "dedup_key": endpoint,
        "payload": {
            "summary": f"{endpoint} is down!",
            "source": "Uptime Monitor",
            "severity": "error"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token token={api_key}"
    }
    url = "https://events.pagerduty.com/v2/enqueue"
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()

def send_slack_alert(endpoint, webhook_url, channel):
    message = f"{endpoint} is down!"
    payload = {
        "channel": channel,
        "text": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, json=payload, headers=headers)
    response.raise_for_status()

def send_alert(endpoint, config):
    current_timestamp = datetime.now().timestamp()
    last_alert_timestamp = last_alert_timestamps.get(endpoint)
    cooldown_duration = config['alerting']['cooldown_duration']

    if last_alert_timestamp is None or (current_timestamp - last_alert_timestamp >= cooldown_duration):
        if config['alerting']['pagerduty']['enabled']:
            send_pagerduty_alert(endpoint, config['alerting']['pagerduty']['api_key'])

        if config['alerting']['slack']['enabled']:
            send_slack_alert(endpoint, config['alerting']['slack']['webhook_url'], config['alerting']['slack']['channel'])

        last_alert_timestamps[endpoint] = current_timestamp



env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)
env.filters['calculate_uptime'] = calculate_uptime
env.filters['calculate_response_time'] = calculate_response_time

def check_for_alert(endpoint, pings, config):
    consecutive_failures_threshold = config['alerting']['consecutive_failures_threshold']
    cooldown_duration = config['alerting']['cooldown_duration']

    if len(pings) >= consecutive_failures_threshold:
        consecutive_failures = sum(not status for status, _ in pings)
        if consecutive_failures >= consecutive_failures_threshold:
            last_alert_timestamp = last_alert_timestamps.get(endpoint)
            current_timestamp = datetime.now().timestamp()
            time_since_last_alert = current_timestamp - last_alert_timestamp if last_alert_timestamp else None

            if time_since_last_alert is None or time_since_last_alert >= cooldown_duration:
                send_alert(endpoint, config)
                last_alert_timestamps[endpoint] = current_timestamp


def send_pings(config):
    while True:
        with app.app_context():
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
                conn = sqlite3.connect(database_path)
                c = conn.cursor()
                c.execute("INSERT INTO pings VALUES (?, ?, ?, ?)",
                          (endpoint, int(status), response_time.total_seconds() if response_time else None, str(datetime.now())))
                conn.commit()
                conn.close()

                check_for_alert(endpoint, ping_history[endpoint], config)

            time.sleep(ping_interval)

@app.route('/')
def home():
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    template = env.get_template('index.html')
    rendered_template = template.render(results=ping_history)

    return render_template_string(rendered_template)

if __name__ == '__main__':
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)
        ping_interval = config.get('ping_interval', 1)

    # Start a separate thread for sending pings
    ping_thread = threading.Thread(target=send_pings, args=(config,))
    ping_thread.daemon = True
    ping_thread.start()

    app.run(debug=True)
