import os
from dotenv import load_dotenv

# Load from .env file if it exists (for local development)
load_dotenv()

class Config:
    # Application Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')  # 'development' or 'production'
    
    # Firebase Configuration
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key-v2'
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
    
    # CORS Configuration - Allow GitHub Pages frontend and local development
    CORS_ORIGINS = [
        'https://nitheshkg.github.io',
        'http://localhost:5173',  # Vite dev server
        'http://localhost:3000',   # Alternative dev server
        'http://localhost:5000',   # Local API
    ]
