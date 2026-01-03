#!/usr/bin/env python3
"""
Script to initialize default admin user for the POS system.
Run this once to create the admin account.
"""

import os
import sys
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import firebase_admin
from firebase_admin import credentials, firestore
from config import Config

def hash_password(password):
    """Hash a password using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hashed.hex()}"

def create_admin_user():
    """Create a default admin user from environment variables."""
    try:
        print("Initializing Gunaa Jewells User...")
        
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
            if not os.path.exists(cred_path):
                print(f"✗ Error: Firebase credentials file not found at {cred_path}")
                return False
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized")
        
        # Get Firestore client
        db = firestore.client()
        
        # Get credentials from environment variables
        username = os.getenv('DEFAULT_USERNAME')
        password = os.getenv('DEFAULT_PASSWORD')
        email = os.getenv('DEFAULT_EMAIL')
        
        if not username or not password:
            print("✗ Error: DEFAULT_USERNAME and DEFAULT_PASSWORD must be set in .env file")
            return False
        
        users_ref = db.collection('users')
        
        # Check if user already exists
        docs = list(users_ref.where('username', '==', username).stream())
        if docs:
            print("✓ User already exists. Skipping creation.")
            return
        
        # Create user
        user_data = {
            'username': username,
            'password_hash': hash_password(password),
            'name': 'Gunaa Jewells',
            'email': email,
            'role': 'admin',
            'isActive': True,
            'createdAt': datetime.now().isoformat(),
            'lastLogin': None,
            'authToken': None,
            'tokenExpiry': None
        }
        
        users_ref.add(user_data)
        
        print("✓ User created successfully!")
        print("\n⚠️  SECURITY NOTE:")
        print("Credentials have been securely created and stored.")
        print("Username and password are NOT displayed for security reasons.")
        
    except Exception as e:
        print(f"✗ Error creating user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    create_admin_user()
