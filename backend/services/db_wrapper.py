"""
Unified database interface for both Firebase (Production) and Local JSON (Development)
This abstraction keeps production code untouched
"""
from flask import current_app
from config import Config

class DBWrapper:
    """Unified database interface - uses Firebase in production, LocalDB in development"""
    
    @staticmethod
    def add(collection, data):
        """Add document to collection"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.add_document(collection, data)
        else:
            # Production: Firebase
            doc_ref = current_app.db.collection(collection).document()
            doc_ref.set(data)
            return doc_ref.id
    
    @staticmethod
    def update(collection, doc_id, data):
        """Update document in collection"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.update_document(collection, doc_id, data)
        else:
            # Production: Firebase
            current_app.db.collection(collection).document(doc_id).update(data)
            return True
    
    @staticmethod
    def delete(collection, doc_id):
        """Delete document from collection"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.delete_document(collection, doc_id)
        else:
            # Production: Firebase
            current_app.db.collection(collection).document(doc_id).delete()
            return True
    
    @staticmethod
    def get_all(collection):
        """Get all documents from collection"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.get_collection(collection)
        else:
            # Production: Firebase
            docs = current_app.db.collection(collection).stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @staticmethod
    def find(collection, field, value):
        """Find single document by field"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.find_document(collection, field, value)
        else:
            # Production: Firebase
            docs = current_app.db.collection(collection).where(field, '==', value).stream()
            for doc in docs:
                return {'id': doc.id, **doc.to_dict()}
            return None
    
    @staticmethod
    def query(collection, filters=None):
        """Query collection with filters"""
        if Config.ENVIRONMENT == 'development':
            return current_app.local_db.query(collection, filters)
        else:
            # Production: Firebase
            query = current_app.db.collection(collection)
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    @staticmethod
    def get_by_id(collection, doc_id):
        """Get document by ID"""
        if Config.ENVIRONMENT == 'development':
            docs = current_app.local_db.get_collection(collection)
            for doc in docs:
                if doc.get('id') == str(doc_id):
                    return doc
            return None
        else:
            # Production: Firebase
            doc = current_app.db.collection(collection).document(doc_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
