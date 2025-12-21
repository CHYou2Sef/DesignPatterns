import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Configuration ---
# Use environment variable for DB URL (Render/Heroku compatible), or default to local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///game_data.db')
# Fix for some postgres URLs starting with "postgres://" instead of "postgresql://"
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security: API Key
API_KEY = os.environ.get('API_KEY', 'my-secret-dev-key') # Default for dev

db = SQLAlchemy(app)

# --- Models ---
class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'username': self.username,
            'score': self.score,
            'timestamp': self.timestamp.isoformat()
        }

# --- Helper Functions ---
def check_api_key():
    """Simple API Key check. Returns True if valid, False otherwise."""
    # Check header or query param or json body
    key = request.headers.get('X-API-KEY') or request.args.get('api_key')
    if not key:
        return False
    return key == API_KEY

# --- Routes ---

@app.route('/')
def home():
    return "API Defender Server is Running!"

@app.route('/log', methods=['POST'])
def log_event():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or 'level' not in data or 'message' not in data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        new_log = GameLog(level=data['level'], message=data['message'])
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"status": "logged", "id": new_log.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # Return Top 10 High Scores
    top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    return jsonify([s.to_dict() for s in top_scores])

@app.route('/score', methods=['POST'])
def submit_score():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    if not data or 'username' not in data or 'score' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    try:
        new_score = Score(username=data['username'], score=data['score'])
        db.session.add(new_score)
        db.session.commit()
        return jsonify({"status": "score saved", "id": new_score.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get game statistics - total logs, total scores, highest score"""
    try:
        total_logs = GameLog.query.count()
        total_scores = Score.query.count()
        highest_score = db.session.query(db.func.max(Score.score)).scalar() or 0
        
        return jsonify({
            "total_logs": total_logs,
            "total_scores": total_scores,
            "highest_score": highest_score
        })
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# --- Setup ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use PORT env variable if available (good for some hosts), default 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
