from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    login_time = db.Column(db.DateTime, default=datetime.now)

    # New ML-ready features
    login_hour = db.Column(db.Integer)
    day_of_week = db.Column(db.Integer)
    ip_address = db.Column(db.String(50))
    ip_group = db.Column(db.String(50))
    device_full = db.Column(db.String(200))
    device_type = db.Column(db.String(50))
