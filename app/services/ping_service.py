from app.models import db, Ping
from app.config import config
import requests
from ping3 import ping
from app.services.alert_service import should_send_alert, send_alert

def ping_endpoints():
    for endpoint_dict in config['endpoints']:
        endpoint = endpoint_dict['url']
        if is_valid_ip_address(endpoint):
            ping_ip_address(endpoint)
        else:
            ping_url(endpoint)

def ping_ip_address(ip_address):
    try:
        response_time = ping(ip_address, timeout=5)
        successful = response_time is not None
    except Exception:
        successful = False

    record_ping(ip_address, successful)

def ping_url(url):
    try:
        response = requests.get(url, timeout=5)
        successful = response.status_code == 200
    except requests.exceptions.RequestException:
        successful = False

    record_ping(url, successful)

def record_ping(endpoint, successful):
    ping = Ping(endpoint=endpoint, successful=successful)
    db.session.add(ping)
    db.session.commit()

    if config['alerting']['enabled']:
        check_and_send_alert(endpoint, successful)

def check_and_send_alert(endpoint, successful):
    if not successful:
        consecutive_failures = Ping.query.filter_by(
            endpoint=endpoint, 
            successful=False
        ).order_by(Ping.sent_time.desc()).limit(
            config['alerting']['consecutive_failures_threshold']
        ).count()

        if consecutive_failures >= config['alerting']['consecutive_failures_threshold']:
            if should_send_alert(endpoint):
                send_alert(endpoint)

def is_valid_ip_address(endpoint):
    parts = endpoint.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or int(part) < 0 or int(part) > 255:
            return False
    return True