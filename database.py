import sqlite3
import os
from datetime import datetime, timedelta


database_path = 'ping_history.db'

def create_database():
    if not os.path.exists(database_path):
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE pings
                     (endpoint TEXT, status INTEGER, response_time FLOAT, timestamp TEXT)''')
        c.execute('''CREATE TABLE users
                     (username TEXT PRIMARY KEY, password TEXT)''')
        conn.commit()
        conn.close()

def store_ping_data(endpoint, status, response_time):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("INSERT INTO pings VALUES (?, ?, ?, ?)",
              (endpoint, int(status), response_time.total_seconds() if response_time else None, str(datetime.now())))
    conn.commit()
    conn.close()

def retrieve_ping_data():
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("SELECT * FROM pings")
    data = c.fetchall()
    conn.close()
    return data

def store_user(username, password):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?)",
              (username, password))
    conn.commit()
    conn.close()

def retrieve_user(username):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user:
        return {'username': user[0], 'password': user[1]}
    else:
        return None
