from flask import request, jsonify, session
from flask_login import login_required
from models import UserPreference, BotLog, db

# ✅ In-memory bot runtime state
bot_runtime_state = {}

def setup_routes(app):
    @app.route('/api/bot/status')
    @login_required
    def bot_status():
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Unauthorized", "message": "Session email missing"}), 401

        prefs = UserPreference.query.filter_by(user_email=email).first()
        return jsonify({
            "running": bot_runtime_state.get(email, False),
            "risk_level": prefs.risk_level if prefs else 2.0,
            "auto_trading": prefs.auto_trading if prefs else True
        })

    @app.route('/api/bot/start', methods=['POST'])
    @login_required
    def bot_start():
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Unauthorized", "message": "Session email missing"}), 401

        bot_runtime_state[email] = True
        return jsonify({"status": "Bot started", "running": True})

    @app.route('/api/bot/stop', methods=['POST'])
    @login_required
    def bot_stop():
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Unauthorized", "message": "Session email missing"}), 401

        bot_runtime_state[email] = False
        return jsonify({"status": "Bot stopped", "running": False})

    @app.route('/api/bot/settings', methods=['PATCH'])
    @login_required
    def bot_settings():
        data = request.json or {}
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Unauthorized", "message": "Session email missing"}), 401

        prefs = UserPreference.query.filter_by(user_email=email).first()
        if not prefs:
            prefs = UserPreference(user_email=email)
            db.session.add(prefs)

        try:
            prefs.risk_level = float(data.get("risk_level", prefs.risk_level))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid risk level"}), 400

        prefs.auto_trading = bool(data.get("auto_trading", prefs.auto_trading))
        db.session.commit()
        return jsonify({
            "status": "Settings updated",
            "risk_level": prefs.risk_level,
            "auto_trading": prefs.auto_trading
        })
