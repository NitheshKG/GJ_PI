from flask import Blueprint, request, jsonify
from services.db import get_db
import hashlib
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def hash_password(password):
    """Hash a password using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hashed.hex()}"

def verify_password(stored_password, provided_password):
    """Verify a password against a stored hash."""
    try:
        salt, hashed = stored_password.split('$')
        provided_hashed = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return provided_hashed.hex() == hashed
    except:
        return False

def generate_token():
    """Generate a simple token for authentication."""
    return secrets.token_urlsafe(32)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return auth token."""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        db = get_db()
        users_ref = db.collection('users')
        
        # Query for user by username
        docs = users_ref.where('username', '==', username).stream()
        user_doc = None
        for doc in docs:
            user_doc = doc
            break
        
        if not user_doc:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user_data = user_doc.to_dict()
        
        # Verify password
        if not verify_password(user_data.get('password_hash', ''), password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if user is active
        if not user_data.get('isActive', True):
            return jsonify({'error': 'User account is disabled'}), 401
        
        # Generate auth token
        token = generate_token()
        token_expiry = datetime.now() + timedelta(days=30)
        
        # Update user with token
        users_ref.document(user_doc.id).update({
            'authToken': token,
            'tokenExpiry': token_expiry.isoformat(),
            'lastLogin': datetime.now().isoformat()
        })
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_doc.id,
                'username': user_data.get('username'),
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'role': user_data.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (admin only)."""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        email = data.get('email')
        
        if not all([username, password, name]):
            return jsonify({'error': 'Username, password, and name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        db = get_db()
        users_ref = db.collection('users')
        
        # Check if username already exists
        docs = list(users_ref.where('username', '==', username).stream())
        if docs:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create new user
        user_data = {
            'username': username,
            'password_hash': hash_password(password),
            'name': name,
            'email': email or '',
            'role': 'user',
            'isActive': True,
            'createdAt': datetime.now().isoformat(),
            'lastLogin': None,
            'authToken': None,
            'tokenExpiry': None
        }
        
        users_ref.add(user_data)
        
        return jsonify({'message': 'User registered successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify if an auth token is valid."""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        db = get_db()
        users_ref = db.collection('users')
        
        # Query for user by token
        docs = users_ref.where('authToken', '==', token).stream()
        user_doc = None
        for doc in docs:
            user_doc = doc
            break
        
        if not user_doc:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_data = user_doc.to_dict()
        
        # Check if token has expired
        if user_data.get('tokenExpiry'):
            expiry = datetime.fromisoformat(user_data['tokenExpiry'])
            if datetime.now() > expiry:
                return jsonify({'error': 'Token has expired'}), 401
        
        # Check if user is active
        if not user_data.get('isActive', True):
            return jsonify({'error': 'User account is disabled'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user_doc.id,
                'username': user_data.get('username'),
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'role': user_data.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user by invalidating token."""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        db = get_db()
        users_ref = db.collection('users')
        
        # Query for user by token
        docs = users_ref.where('authToken', '==', token).stream()
        user_doc = None
        for doc in docs:
            user_doc = doc
            break
        
        if user_doc:
            users_ref.document(user_doc.id).update({
                'authToken': None,
                'tokenExpiry': None
            })
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password."""
    try:
        data = request.json
        token = data.get('token')
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')
        
        if not all([token, old_password, new_password]):
            return jsonify({'error': 'Token, old password, and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        db = get_db()
        users_ref = db.collection('users')
        
        # Query for user by token
        docs = users_ref.where('authToken', '==', token).stream()
        user_doc = None
        for doc in docs:
            user_doc = doc
            break
        
        if not user_doc:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_data = user_doc.to_dict()
        
        # Verify old password
        if not verify_password(user_data.get('password_hash', ''), old_password):
            return jsonify({'error': 'Old password is incorrect'}), 401
        
        # Update password
        users_ref.document(user_doc.id).update({
            'password_hash': hash_password(new_password)
        })
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
