from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import timedelta
from extensions import db, bcrypt

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Create instance folder if it doesn't exist
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Use instance folder for database (more persistent)
default_db_path = f'sqlite:///{os.path.join(instance_path, "database.db")}'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration (24 hour timeout)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Initialize extensions with app
db.init_app(app)
bcrypt.init_app(app)

# CORS configuration for frontend (localhost:5173)
CORS(app,
     origins=['http://localhost:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Import models (must be after db initialization)
import models

# Import and register routes
from routes.auth import auth_bp
from routes.generate import generate_bp
from routes.materials import materials_bp
from routes.export import export_bp

app.register_blueprint(auth_bp)
app.register_blueprint(generate_bp)
app.register_blueprint(materials_bp)
app.register_blueprint(export_bp)

# Test route
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running'
    }), 200

if __name__ == '__main__':
    # Run the Flask app
    # Note: Run init_db.py first to create database tables
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
