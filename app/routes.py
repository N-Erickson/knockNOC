from flask import Blueprint, jsonify, render_template
from app.models import Ping
from app.config import config
import logging
import traceback

main = Blueprint('main', __name__)
logging.basicConfig(level=logging.DEBUG)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/pings')
def api_pings():
    try:
        endpoints = config['endpoints']
        pings = []
        for endpoint_dict in endpoints:
            endpoint = endpoint_dict['url']
            display_name = endpoint_dict.get('display_name', endpoint)
            endpoint_pings = Ping.query.filter_by(endpoint=endpoint).order_by(Ping.sent_time.desc()).limit(100).all()
            pings.append({
                'endpoint': endpoint,
                'display_name': display_name,
                'pings': [{
                    'sent_time': str(ping.sent_time),
                    'received_time': str(ping.received_time),
                    'successful': ping.successful,
                } for ping in endpoint_pings]
            })
        return jsonify(pings)
    except Exception as e:
        logging.error(f"Error in api_pings: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500