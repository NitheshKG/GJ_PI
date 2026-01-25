import firebase_admin
from firebase_admin import credentials, firestore
import os

_db = None

def init_db(app):
    """Initialize Firebase Firestore."""
    global _db
    
    # Check if already initialized
    if not firebase_admin._apps:
        cred_path = app.config.get('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
        
        # In Cloud Run, try to use Application Default Credentials first
        # This uses the service account attached to the Cloud Run service
        try:
            if os.path.exists(cred_path):
                # Local development or if credentials file exists
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("✓ Firebase initialized with certificate")
            else:
                # Cloud Run and production - use ADC
                firebase_admin.initialize_app()
                print("✓ Firebase initialized with Application Default Credentials")
        except FileNotFoundError:
            # Fallback to Application Default Credentials
            firebase_admin.initialize_app()
            print("✓ Firebase initialized with Application Default Credentials (fallback)")
    
    _db = firestore.client()
    print("✓ Firestore client initialized")
    
    return _db

def get_db():
    """Get Firestore database instance."""
    return _db
