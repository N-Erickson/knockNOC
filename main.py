import os
import requests
import yaml
from flask import Flask, render_template, request, redirect, session, url_for
from jinja2 import select_autoescape, Environment, FileSystemLoader
from datetime import datetime, timedelta
import sqlite3
import json
import time
import threading
from collections import deque
from monitoring import ping_history, calculate_uptime, calculate_response_time, check_for_alert
import database

app = Flask(__name__)

# Load configuration from YAML file
config = {}
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Set up Jinja2 template environment
template_loader = FileSystemLoader(searchpath=os.path.abspath("templates"))
template_env = Environment(loader=template_loader, autoescape=select_autoescape(['html', 'xml']))
template_env.filters['calculate_response_time'] = calculate_response_time

# Register custom filters
template_env.filters['calculate_uptime'] = calculate_uptime

# Load the template
template = template_env.get_template('index.html')

# Ping interval in seconds
ping_interval = config['ping_interval']

# Database initialization logic here
database.create_database()

def store_ping_data(endpoint, status, response_time):
    # Store ping data in the database logic here
    database.store_ping_data(endpoint, status, response_time)

@app.route('/')
def home():
    if 'username' in session:
        rendered_template = template.render(results=ping_history, url_for=url_for, session=session)
        return rendered_template
    else:
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            # Store the username and password in the database (you can use a separate table for user authentication)
            # Example: database.store_user(username, password)
            # Replace the example code with the actual logic for storing user information
            session['username'] = username
            return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            # Retrieve the user from the database (you can use a separate table for user authentication)
            # Example: user = database.retrieve_user(username)
            # Replace the example code with the actual logic for retrieving user information
            # if user and user.password == password:
            #     session['username'] = username
            if username == 'admin' and password == 'admin':
                session['username'] = username
                return redirect('/')
    return render_template('login.html')

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

    app.secret_key = 'secret_key'
    app.run(debug=True)
