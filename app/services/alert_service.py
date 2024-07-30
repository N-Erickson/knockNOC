import requests
import json
from datetime import datetime, timedelta
from app.config import config

last_alert_times = {}

def should_send_alert(endpoint):
    cooldown_duration = config['alerting']['cooldown_duration']
    last_alert_time = last_alert_times.get(endpoint)
    if last_alert_time is None or datetime.now() - last_alert_time >= timedelta(seconds=cooldown_duration):
        last_alert_times[endpoint] = datetime.now()
        return True
    return False

def send_alert(endpoint):
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

def send_pagerduty_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Token token={config['alerting']['pagerduty']['api_key']}",
    }

    data = {
        'incident': {
            'type': 'incident',
            'title': f'Failed to ping endpoint: {endpoint}',
            'service': {
                'id': config['alerting']['pagerduty']['service_id'],
                'type': 'service_reference',
            },
        },
    }

    response = requests.post('https://api.pagerduty.com/incidents', headers=headers, json=data)
    print(f"PagerDuty alert sent for {endpoint}. Status: {response.status_code}")

def send_opsgenie_alert(endpoint):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"GenieKey {config['alerting']['opsgenie']['api_key']}",
    }

    data = {
        'message': f'Failed to ping endpoint: {endpoint}',
        'description': f'The endpoint {endpoint} is not responding to pings.',
    }

    response = requests.post('https://api.opsgenie.com/v2/alerts', headers=headers, json=data)
    print(f"OpsGenie alert sent for {endpoint}. Status: {response.status_code}")

def send_slack_alert(endpoint):
    data = {
        'text': f'Failed to ping endpoint: {endpoint}',
    }

    response = requests.post(config['alerting']['slack']['webhook_url'], json=data)
    print(f"Slack alert sent for {endpoint}. Status: {response.status_code}")

def send_telegram_alert(endpoint):
    url = f"https://api.telegram.org/bot{config['alerting']['telegram']['bot_token']}/sendMessage"

    data = {
        'chat_id': config['alerting']['telegram']['chat_id'],
        'text': f'Failed to ping endpoint: {endpoint}',
    }

    response = requests.post(url, data=data)
    print(f"Telegram alert sent for {endpoint}. Status: {response.status_code}")

def send_discord_alert(endpoint):
    data = {
        'content': f'Failed to ping endpoint: {endpoint}',
    }

    response = requests.post(config['alerting']['discord']['webhook_url'], json=data)
    print(f"Discord alert sent for {endpoint}. Status: {response.status_code}")