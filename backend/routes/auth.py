"""
Authentication routes
Handles user registration, login, and logout
"""
from flask import Blueprint, request, jsonify, session
from extensions import db, bcrypt
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password (minimum 6 characters)"""
    return len(password) >= 6

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    Request body: { "email": "user@example.com", "password": "password123" }
    """
    from models import User

    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Email and password are required'
            }), 400

        email = data['email'].strip().lower()
        password = data['password']

        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email format'
            }), 400

        if not validate_password(password):
            return jsonify({
                'error': 'Password must be at least 6 characters long'
            }), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'error': 'User with this email already exists'
            }), 409

        # Hash password with bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            email=email,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['user_email'] = new_user.email

        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'created_at': new_user.created_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'details': str(e)
        }), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login user
    Request body: { "email": "user@example.com", "password": "password123" }
    """
    from models import User

    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'error': 'Email and password are required'
            }), 400

        email = data['email'].strip().lower()
        password = data['password']

        user = User.query.filter_by(email=email).first()

        # Verify user exists and password is correct
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({
                'error': 'Invalid email or password'
            }), 401

        session['user_id'] = user.id
        session['user_email'] = user.email

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'details': str(e)
        }), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Logout user (destroy session)
    """
    try:
        if 'user_id' not in session:
            return jsonify({
                'error': 'No active session'
            }), 401

        session.clear()

        return jsonify({
            'message': 'Logout successful'
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Logout failed',
            'details': str(e)
        }), 500

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """
    Get current logged in user info
    """
    from models import User

    try:
        if 'user_id' not in session:
            return jsonify({
                'error': 'Not authenticated'
            }), 401

        user = User.query.get(session['user_id'])

        if not user:
            session.clear()
            return jsonify({
                'error': 'User not found'
            }), 404

        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get user info',
            'details': str(e)
        }), 500
