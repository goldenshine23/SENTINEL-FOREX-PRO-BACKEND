from flask import Flask, jsonify  # Added jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS  # ✅ Added CORS
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

# ✅ Create Flask app instance
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///mt5bot.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Enable CORS for frontend communication
CORS(app)

# ✅ Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

# ✅ Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)

# ✅ Import and register models AFTER initializing db
from models import User

# ✅ Create tables if not existing
with app.app_context():
    db.create_all()

# ✅ Register routes
from routes import setup_routes
setup_routes(app)

# ✅ ✅ Place test route AFTER custom routes to prevent overrides
@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Flask backend!"})

# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True)
