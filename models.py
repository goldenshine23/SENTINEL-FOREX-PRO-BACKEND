from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize db here; call db.init_app(app) in app.py
db = SQLAlchemy()

# -------------------------------
# User Model
# -------------------------------
class User(db.Model):
    __tablename__ = 'users'

    email = db.Column(db.String(120), primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    telegram_username = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='user', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('BotLog', backref='user', lazy=True, cascade='all, delete-orphan')


# -------------------------------
# Trade Model
# -------------------------------
class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    symbol = db.Column(db.String(20))
    type = db.Column(db.String(10))  # 'buy' or 'sell'
    lot = db.Column(db.Float)
    profit = db.Column(db.Float)
    time_opened = db.Column(db.DateTime, default=datetime.utcnow)
    time_closed = db.Column(db.DateTime, nullable=True)


# -------------------------------
# Bot Log Model
# -------------------------------
class BotLog(db.Model):
    __tablename__ = 'bot_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    log_line = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------------
# User Preferences Model
# -------------------------------
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False, unique=True)
    risk_level = db.Column(db.Float, default=2.0)
    auto_trading = db.Column(db.Boolean, default=True)
    show_trade_history = db.Column(db.Boolean, default=True)
    show_news = db.Column(db.Boolean, default=True)
    show_calendar = db.Column(db.Boolean, default=True)
    dark_mode = db.Column(db.Boolean, default=False)
