from app import db
from datetime import datetime

class Ping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False)
    sent_time = db.Column(db.DateTime, default=datetime.utcnow)
    received_time = db.Column(db.DateTime)
    successful = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Ping {self.endpoint} at {self.sent_time}>'