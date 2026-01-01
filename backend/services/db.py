import firebase_admin
from firebase_admin import credentials, firestore

_db = None

def init_db(app):
    """Initialize Firebase Firestore."""
    global _db
    
    # Check if already initialized
    if not firebase_admin._apps:
        cred_path = app.config.get('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✓ Firebase initialized (Firestore only)")
    
    _db = firestore.client()
    print("✓ Firestore client initialized")
    
    return _db

def get_db():
    """Get Firestore database instance."""
    return _db
