from datetime import datetime
from collections import deque
import alerting

ping_history = {}

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

def check_for_alert(endpoint, pings, config):
    consecutive_failures_threshold = config['alerting']['consecutive_failures_threshold']
    cooldown_duration = config['alerting']['cooldown_duration']

    if len(pings) >= consecutive_failures_threshold:
        consecutive_failures = sum(status is False for status, _ in pings)

        if consecutive_failures >= consecutive_failures_threshold:
            # Perform alerting logic here
            alerting.send_alert(endpoint, config)

def ping_endpoint(endpoint):
    # Perform the ping request and return the result
    pass

def monitor_endpoint(endpoint, config):
    ping_interval = config['ping_interval']
    ping_history[endpoint] = deque(maxlen=config['alerting']['consecutive_failures_threshold'])

    while True:
        status = ping_endpoint(endpoint)
        ping_history[endpoint].append((status, datetime.now()))

        check_for_alert(endpoint, ping_history[endpoint], config)

        time.sleep(ping_interval)
