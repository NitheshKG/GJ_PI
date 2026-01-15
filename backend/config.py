import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Firebase Configuration
    # In production, we strictly require SECRET_KEY to be set
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY and os.getenv('FLASK_ENV') == 'production':
        raise ValueError("No SECRET_KEY set for production configuration")
        
    # Fallback for dev only
    if not SECRET_KEY:
        SECRET_KEY = 'dev-secret-key'
        
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
