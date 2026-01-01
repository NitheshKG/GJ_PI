import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Firebase Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
