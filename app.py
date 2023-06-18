import os
import yaml
import sqlite3
import requests
import json
from flask import Flask, render_template, g, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from ping3 import ping

# Load configuration from YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create Flask app
app = Flask(__name__)

# Function to create the database and table if they don't exist
def create_database():
    conn = sqlite3.connect('pings.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS pings (
            id INTEGER PRIMARY KEY,
            endpoint TEXT,
            sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            received_time TIMESTAMP,
            successful BOOLEAN
        )
    ''')

    conn.commit()
    conn.close()

# Run the function to create the database
create_database()

# Create database if it doesn't exist
conn = sqlite3.connect('pings.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS pings (
        id INTEGER PRIMARY KEY,
        endpoint TEXT,
        sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        received_time TIMESTAMP,
        successful BOOLEAN
    )
''')
conn.commit()
conn.close()

# Dictionary to track last alert time for each endpoint
last_alert_times = {}

# Function to ping IP addresses
def ping_ip_address(ip_address):
    try:
        response_time = ping(ip_address, timeout=5)
        successful = response_time is not None
    except Exception:
        successful = False

    conn = sqlite3.connect('pings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO pings (endpoint, successful) VALUES (?, ?)
    ''', (ip_address, successful))
    conn.commit()

    # Check if alerting is enabled
    if config['alerting']['enabled']:
        # Check if the ping was unsuccessful
        if not successful:
            # Count the number of consecutive failures
            c.execute('''
                SELECT COUNT(*) FROM (
                    SELECT successful FROM pings
                    WHERE endpoint = ?
                    ORDER BY sent_time DESC
                    LIMIT ?
                )
                WHERE successful = 0
            ''', (ip_address, config['alerting']['consecutive_failures_threshold']))
            consecutive_failures = c.fetchone()[0]

            # If the number of consecutive failures is above the threshold and cooldown duration has passed, send an alert
            if consecutive_failures >= config['alerting']['consecutive_failures_threshold']:
                if should_send_alert(ip_address):
                    send_alert(ip_address)

    conn.close()

# Function to ping URLs
def ping_url(url):
    try:
        response = requests.get(url, timeout=5)
        successful = response.status_code == 200
    except requests.exceptions.RequestException:
        successful = False

    conn = sqlite3.connect('pings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO pings (endpoint, successful) VALUES (?, ?)
    ''', (url, successful))
    conn.commit()

    # Check if alerting is enabled
    if config['alerting']['enabled']:
        # Check if the ping was unsuccessful
        if not successful:
            # Count the number of consecutive failures
            c.execute('''
                SELECT COUNT(*) FROM (
                    SELECT successful FROM pings
                    WHERE endpoint = ?
                    ORDER BY sent_time DESC
                    LIMIT ?
                )
                WHERE successful = 0
            ''', (url, config['alerting']['consecutive_failures_threshold']))
            consecutive_failures = c.fetchone()[0]

            # If the number of consecutive failures is above the threshold and cooldown duration has passed, send an alert
            if consecutive_failures >= config['alerting']['consecutive_failures_threshold']:
                if should_send_alert(url):
                    send_alert(url)

    conn.close()

# Function to ping endpoints
def ping_endpoints():
    for endpoint_dict in config['endpoints']:
        endpoint = endpoint_dict['url']
        if is_valid_ip_address(endpoint):
            ping_ip_address(endpoint)
        else:
            ping_url(endpoint)

# Function to check if an alert should be sent based on cooldown duration
def should_send_alert(endpoint):
    cooldown_duration = config['alerting']['cooldown_duration']
    last_alert_time = last_alert_times.get(endpoint)
    if last_alert_time is None or datetime.now() - last_alert_time >= timedelta(seconds=cooldown_duration):
        last_alert_times[endpoint] = datetime.now()
        return True
    return False

# Function to send an alert
def send_alert(endpoint):
    # Check which alerting services are enabled and send an alert to each one
    if config['alerting']['pagerduty']['enabled']:
        send_pagerduty_alert(endpoint)
    if config['alerting']['opsgenie']['enabled']:
        send_opsgenie_alert(endpoint)
    if config['alerting']['slack']['enabled']:
        send_slack_alert(endpoint)
    if config['alerting']['telegram']['enabled']:
        send_telegram_alert(endpoint)
    if config['alerting']['discord']['enabled']:
        send_discord_alert(endpoint)

# Function to send alert to PagerDuty
def send_pagerduty_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token token={token}'.format(token=config['alerting']['pagerduty']['api_key']),
    }

    data = {
        'incident': {
            'type': 'incident',
            'title': 'Failed to ping endpoint: {endpoint}'.format(endpoint=endpoint),
            'service': {
                'id': config['alerting']['pagerduty']['service_id'],
                'type': 'service_reference',
            },
        },
    }

    response = requests.post('https://api.pagerduty.com/incidents', headers=headers, data=json.dumps(data))

# Function to send alert to OpsGenie
def send_opsgenie_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'GenieKey {api_key}'.format(api_key=config['alerting']['opsgenie']['api_key']),
    }

    data = {
        'message': 'Failed to ping endpoint: {endpoint}'.format(endpoint=endpoint),
        'description': 'The endpoint {endpoint} is not responding to pings.'.format(endpoint=endpoint),
    }

    response = requests.post('https://api.opsgenie.com/v2/alerts', headers=headers, data=json.dumps(data))

# Function to send alert to Slack
def send_slack_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'text': 'Failed to ping endpoint: {endpoint}'.format(endpoint=endpoint),
    }

    response = requests.post(config['alerting']['slack']['webhook_url'], headers=headers, data=json.dumps(data))

# Function to send alert to Telegram
def send_telegram_alert(endpoint):
    url = "https://api.telegram.org/bot{token}/sendMessage".format(token=config['alerting']['telegram']['bot_token'])

    data = {
        'chat_id': config['alerting']['telegram']['chat_id'],
        'text': 'Failed to ping endpoint: {endpoint}'.format(endpoint=endpoint),
    }

    response = requests.post(url, data=data)

# Function to send alert to Discord
def send_discord_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'content': 'Failed to ping endpoint: {endpoint}'.format(endpoint=endpoint),
    }

    response = requests.post(config['alerting']['discord']['webhook_url'], headers=headers, data=json.dumps(data))

# Function to check if an endpoint is a valid IP address
def is_valid_ip_address(endpoint):
    parts = endpoint.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or int(part) < 0 or int(part) > 255:
            return False
    return True

# Schedule the function to ping endpoints every 5 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(ping_endpoints, 'interval', seconds=5)
scheduler.start()

@app.route('/')
def index():
    conn = sqlite3.connect('pings.db')
    c = conn.cursor()
    endpoints = config['endpoints']

    pings = []
    for endpoint_dict in endpoints:
        endpoint = endpoint_dict['url']
        display_name = endpoint_dict.get('display_name', endpoint)
        c.execute('''
            SELECT sent_time, received_time, successful FROM pings
            WHERE endpoint = ?
            ORDER BY sent_time DESC
            LIMIT 100
        ''', (endpoint,))
        endpoint_pings = c.fetchall()
        pings.append({
            'endpoint': endpoint,
            'display_name': display_name,
            'pings': [{
                'sent_time': str(ping[0]),
                'received_time': str(ping[1]),
                'successful': bool(ping[2]),
            } for ping in endpoint_pings]
        })
    conn.close()

    return render_template('index.html', pings=pings)

@app.route('/api/pings')
def api_pings():
    conn = sqlite3.connect('pings.db')
    c = conn.cursor()
    endpoints = config['endpoints']

    pings = []
    for endpoint_dict in endpoints:
        endpoint = endpoint_dict['url']
        display_name = endpoint_dict.get('display_name', endpoint)
        c.execute('''
            SELECT sent_time, received_time, successful FROM pings
            WHERE endpoint = ?
            ORDER BY sent_time DESC
            LIMIT 100
        ''', (endpoint,))
        endpoint_pings = c.fetchall()
        pings.append({
            'endpoint': endpoint,
            'display_name': display_name,
            'pings': [{
                'sent_time': str(ping[0]),
                'received_time': str(ping[1]),
                'successful': bool(ping[2]),
            } for ping in endpoint_pings]
        })
    conn.close()

    return jsonify(pings)

if __name__ == '__main__':
    app.run(debug=True)
