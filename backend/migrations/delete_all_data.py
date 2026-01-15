import sys
import os

# Add the backend directory to the python path to allow imports from services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db import init_db
from flask import Flask

app = Flask(__name__)

# Initialize Firebase
# This assumes the script is run where it can find the serviceAccountKey.json if needed
# or that FIREBASE_CREDENTIALS_PATH is set correctly in Config or defaults.
init_app = init_db(app)
db = init_app

def delete_collection(coll_ref, batch_size=400):
    """
    Delete all documents in a collection in batches.
    """
    docs = list(coll_ref.limit(batch_size).stream())
    deleted = 0

    if not docs:
        return 0

    while docs:
        batch = db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
        
        batch.commit()
        deleted += count
        print(f"  Deleted {count} documents...")
        
        # Get next batch
        docs = list(coll_ref.limit(batch_size).stream())
    
    return deleted

def delete_all_data():
    """
    Delete all data from specific collections.
    """
    # Collections to wipe
    collections_to_wipe = ['customers', 'tickets', 'payments', 'alert_messages']
    
    print("WARNING: This script will PERMANENTLY DELETE all data from the following collections:")
    for col in collections_to_wipe:
        print(f" - {col}")
    print("The 'users' collection will NOT be affected.")
    print("-" * 50)
    
    confirm = input("Type 'DELETE' to confirm and proceed: ")
    if confirm != 'DELETE':
        print("Operation cancelled.")
        return

    print("\nStarting data deletion...")
    
    total_deleted_docs = 0
    
    for collection_name in collections_to_wipe:
        print(f"\nProcessing collection: {collection_name}")
        coll_ref = db.collection(collection_name)
        
        # Check if collection is empty (optimization)
        # Note: In Firestore, collections don't explicitly exist, so we just try to get docs
        
        deleted_count = delete_collection(coll_ref)
        print(f"Done. Removed {deleted_count} documents from '{collection_name}'.")
        total_deleted_docs += deleted_count

    print("-" * 50)
    print(f"Data reset complete. Total documents deleted: {total_deleted_docs}")

if __name__ == '__main__':
    try:
        delete_all_data()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
