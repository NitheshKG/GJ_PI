"""
Local JSON-based database for development
This is only used when ENVIRONMENT=development
Production always uses Firebase
"""
import json
import os
from datetime import datetime
from pathlib import Path

class LocalDB:
    """Mock database using JSON files for local development only"""
    
    def __init__(self):
        self.db_dir = Path('local_data')
        self.db_dir.mkdir(exist_ok=True)
        self._init_collections()
    
    def _init_collections(self):
        """Initialize JSON files for each collection"""
        collections = {
            'users': [],
            'customers': [],
            'tickets': [],
            'payments': [],
            'reports': []
        }
        
        for name, default_data in collections.items():
            filepath = self.db_dir / f'{name}.json'
            if not filepath.exists():
                self._write_file(filepath, default_data)
    
    def _read_file(self, filepath):
        """Read JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _write_file(self, filepath, data):
        """Write to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_collection(self, collection_name):
        """Get all documents from collection"""
        filepath = self.db_dir / f'{collection_name}.json'
        return self._read_file(filepath)
    
    def add_document(self, collection_name, data):
        """Add document to collection"""
        filepath = self.db_dir / f'{collection_name}.json'
        documents = self._read_file(filepath)
        
        # Add ID and timestamp
        doc_id = str(len(documents) + 1)
        data['id'] = doc_id
        data['created_at'] = datetime.now().isoformat()
        
        documents.append(data)
        self._write_file(filepath, documents)
        return doc_id
    
    def update_document(self, collection_name, doc_id, data):
        """Update document in collection"""
        filepath = self.db_dir / f'{collection_name}.json'
        documents = self._read_file(filepath)
        
        for doc in documents:
            if doc.get('id') == str(doc_id):
                doc.update(data)
                doc['updated_at'] = datetime.now().isoformat()
                self._write_file(filepath, documents)
                return True
        
        return False
    
    def delete_document(self, collection_name, doc_id):
        """Delete document from collection"""
        filepath = self.db_dir / f'{collection_name}.json'
        documents = self._read_file(filepath)
        
        documents = [doc for doc in documents if doc.get('id') != str(doc_id)]
        self._write_file(filepath, documents)
    
    def find_document(self, collection_name, field, value):
        """Find document by field"""
        filepath = self.db_dir / f'{collection_name}.json'
        documents = self._read_file(filepath)
        
        for doc in documents:
            if doc.get(field) == value:
                return doc
        
        return None
    
    def query(self, collection_name, filters=None):
        """Query collection with filters"""
        filepath = self.db_dir / f'{collection_name}.json'
        documents = self._read_file(filepath)
        
        if not filters:
            return documents
        
        # Simple filter matching
        results = []
        for doc in documents:
            match = True
            for key, value in filters.items():
                if doc.get(key) != value:
                    match = False
                    break
            if match:
                results.append(doc)
        
        return results
    
    def collection(self, collection_name):
        """Return a collection reference (Firebase-like API)"""
        return CollectionReference(self, collection_name)


class CollectionReference:
    """Mimics Firebase CollectionReference for local development"""
    
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name
    
    def where(self, field, op, value):
        """Query documents where field matches value"""
        return QueryReference(self.db, self.collection_name, field, op, value)
    
    def document(self, doc_id=None):
        """Get a document reference"""
        return DocumentReference(self.db, self.collection_name, doc_id)
    
    def add(self, data):
        """Add a new document"""
        return self.db.add_document(self.collection_name, data)
    
    def stream(self):
        """Stream all documents"""
        documents = self.db.get_collection(self.collection_name)
        return [DocumentSnapshot(doc, doc.get('id')) for doc in documents]


class QueryReference:
    """Mimics Firebase Query for local development"""
    
    def __init__(self, db, collection_name, field, op, value, limit_val=None):
        self.db = db
        self.collection_name = collection_name
        self.field = field
        self.op = op
        self.value = value
        self.limit_val = limit_val
    
    def limit(self, num):
        """Limit query results"""
        return QueryReference(self.db, self.collection_name, self.field, self.op, self.value, num)
    
    def stream(self):
        """Stream query results"""
        documents = self.db.get_collection(self.collection_name)
        results = []
        
        for doc in documents:
            if self.op == '==' and doc.get(self.field) == self.value:
                results.append(DocumentSnapshot(doc, doc.get('id')))
            
            if self.limit_val and len(results) >= self.limit_val:
                break
        
        return results


class DocumentReference:
    """Mimics Firebase DocumentReference for local development"""
    
    def __init__(self, db, collection_name, doc_id=None):
        self.db = db
        self.collection_name = collection_name
        self.doc_id = doc_id or self._generate_id()
    
    @property
    def id(self):
        """Get document ID"""
        return self.doc_id
    
    def _generate_id(self):
        """Generate a unique document ID"""
        import uuid
        return str(uuid.uuid4())
    
    def set(self, data):
        """Set document data"""
        filepath = self.db.db_dir / f'{self.collection_name}.json'
        documents = self.db._read_file(filepath)
        
        # Check if document already exists
        found = False
        for doc in documents:
            if doc.get('id') == self.doc_id:
                doc.update(data)
                found = True
                break
        
        # If not found, add new document
        if not found:
            data_with_id = {'id': self.doc_id}
            data_with_id.update(data)
            data_with_id['createdAt'] = datetime.now().isoformat()
            documents.append(data_with_id)
        
        self.db._write_file(filepath, documents)
        return self
    
    def update(self, data):
        """Update document"""
        return self.db.update_document(self.collection_name, self.doc_id, data)
    
    def get(self):
        """Get document"""
        documents = self.db.get_collection(self.collection_name)
        for doc in documents:
            if doc.get('id') == str(self.doc_id):
                return DocumentSnapshot(doc, self.doc_id)
        return None


class DocumentSnapshot:
    """Mimics Firebase DocumentSnapshot for local development"""
    
    def __init__(self, data, doc_id):
        self.data = data
        self.id = doc_id
    
    @property
    def exists(self):
        """Check if document exists"""
        return self.data is not None
    
    def to_dict(self):
        """Convert to dictionary"""
        return self.data.copy()
    
    def get(self, field):
        """Get field value"""
        return self.data.get(field)

# Global instance
local_db = LocalDB()
