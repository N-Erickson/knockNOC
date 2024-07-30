from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import config

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pings.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    def scheduled_ping_endpoints():
        with app.app_context():
            from app.services.ping_service import ping_endpoints as ping_service
            ping_service()

    scheduler.add_job(scheduled_ping_endpoints, 'interval', seconds=config['ping_frequency'])
    scheduler.start()

    return app