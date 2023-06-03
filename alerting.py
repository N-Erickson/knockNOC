import requests
import json
from datetime import datetime

last_alert_timestamps = {}

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

def send_opsgenie_alert(endpoint, api_key):
    payload = {
        "message": f"{endpoint} is down!",
        "alias": endpoint,
        "source": "Uptime Monitor",
        "priority": "P1"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"GenieKey {api_key}"
    }
    url = "https://api.opsgenie.com/v2/alerts"
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()

def send_telegram_alert(endpoint, token, chat_id):
    message = f"{endpoint} is down!"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json=payload)
    response.raise_for_status()

def send_discord_alert(endpoint, webhook_url):
    message = f"{endpoint} is down!"
    payload = {
        "content": message
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

        if config['alerting']['opsgenie']['enabled']:
            send_opsgenie_alert(endpoint, config['alerting']['opsgenie']['api_key'])

        if config['alerting']['telegram']['enabled']:
            send_telegram_alert(endpoint, config['alerting']['telegram']['token'], config['alerting']['telegram']['chat_id'])

        if config['alerting']['discord']['enabled']:
            send_discord_alert(endpoint, config['alerting']['discord']['webhook_url'])

        last_alert_timestamps[endpoint] = current_timestamp
