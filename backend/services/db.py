import os
from config import Config

_db = None

def init_db(app):
    """Initialize database based on environment"""
    global _db
    
    # Development: Use local JSON-based database (free, no Firebase needed)
    if Config.ENVIRONMENT == 'development':
        from services.local_db import local_db
        app.local_db = local_db
        # Set _db to local_db for get_db() compatibility
        _db = local_db
        print("✓ Local database initialized (JSON files - Development Mode)", flush=True)
        return local_db
    
    # Production: Use Firebase
    import firebase_admin
    from firebase_admin import credentials, firestore
    
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
                print("✓ Firebase initialized with certificate (Production Mode)", flush=True)
            else:
                # Cloud Run and production - use ADC
                firebase_admin.initialize_app()
                print("✓ Firebase initialized with Application Default Credentials (Production Mode)", flush=True)
        except FileNotFoundError:
            # Fallback to Application Default Credentials
            firebase_admin.initialize_app()
            print("✓ Firebase initialized with Application Default Credentials (fallback)", flush=True)
    
    _db = firestore.client()
    app.db = _db
    print("✓ Firestore client initialized (Production Mode)", flush=True)
    
    return _db

def get_db():
    """Get database instance (Firebase for production, LocalDB for development)."""
    return _db
