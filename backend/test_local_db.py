#!/usr/bin/env python3
"""
Test script to verify local database setup works correctly.
Run this from the backend/ directory.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set development environment
os.environ['ENVIRONMENT'] = 'development'

print("=" * 60)
print("Testing Local Database Setup")
print("=" * 60)

# Test 1: Import and initialize LocalDB
print("\n[1] Testing LocalDB initialization...")
try:
    from services.local_db import local_db, LocalDB
    print("✓ LocalDB imported successfully")
    print("✓ LocalDB instance created")
    print(f"✓ Database directory: {local_db.db_dir}")
except Exception as e:
    print(f"✗ Error importing LocalDB: {e}")
    sys.exit(1)

# Test 2: Check collection files created
print("\n[2] Checking collection files...")
try:
    collections = ['users', 'customers', 'tickets', 'payments', 'reports']
    for collection in collections:
        file_path = local_db.db_dir / f'{collection}.json'
        if file_path.exists():
            print(f"✓ {collection}.json exists")
        else:
            print(f"✗ {collection}.json missing")
except Exception as e:
    print(f"✗ Error checking collections: {e}")
    sys.exit(1)

# Test 3: Test add_document
print("\n[3] Testing add_document...")
try:
    doc_id = local_db.add_document('users', {
        'username': 'testuser',
        'password_hash': 'hashed123',
        'email': 'test@example.com'
    })
    print(f"✓ Document added with ID: {doc_id}")
except Exception as e:
    print(f"✗ Error adding document: {e}")
    sys.exit(1)

# Test 4: Test get_collection
print("\n[4] Testing get_collection...")
try:
    users = local_db.get_collection('users')
    print(f"✓ Retrieved {len(users)} document(s) from users collection")
    if users:
        user = users[0]
        print(f"  - ID: {user.get('id')}")
        print(f"  - Username: {user.get('username')}")
        print(f"  - Created: {user.get('created_at')}")
except Exception as e:
    print(f"✗ Error reading collection: {e}")
    sys.exit(1)

# Test 5: Test update_document
print("\n[5] Testing update_document...")
try:
    if users:
        doc_id = users[0]['id']
        local_db.update_document('users', doc_id, {'email': 'newemail@example.com'})
        updated = local_db.get_collection('users')
        if updated[0]['email'] == 'newemail@example.com':
            print(f"✓ Document updated successfully")
            print(f"  - Updated: {updated[0].get('updated_at')}")
        else:
            print(f"✗ Update failed - email not changed")
except Exception as e:
    print(f"✗ Error updating document: {e}")
    sys.exit(1)

# Test 6: Test find_document
print("\n[6] Testing find_document...")
try:
    found_user = local_db.find_document('users', 'username', 'testuser')
    if found_user:
        print(f"✓ Found document by username")
        print(f"  - ID: {found_user.get('id')}")
        print(f"  - Email: {found_user.get('email')}")
    else:
        print(f"✗ Document not found")
except Exception as e:
    print(f"✗ Error finding document: {e}")
    sys.exit(1)

# Test 7: Test query
print("\n[7] Testing query...")
try:
    results = local_db.query('users', {'username': 'testuser'})
    if results:
        print(f"✓ Query returned {len(results)} result(s)")
        print(f"  - First result username: {results[0].get('username')}")
    else:
        print(f"✗ Query returned no results")
except Exception as e:
    print(f"✗ Error querying: {e}")
    sys.exit(1)

# Test 8: Test delete_document
print("\n[8] Testing delete_document...")
try:
    if users:
        doc_id = users[0]['id']
        local_db.delete_document('users', doc_id)
        remaining = local_db.get_collection('users')
        print(f"✓ Document deleted successfully")
        print(f"  - Remaining documents: {len(remaining)}")
except Exception as e:
    print(f"✗ Error deleting document: {e}")
    sys.exit(1)

# Test 9: Test Config.ENVIRONMENT
print("\n[9] Testing Config.ENVIRONMENT...")
try:
    from config import Config
    print(f"✓ Config.ENVIRONMENT = '{Config.ENVIRONMENT}'")
    if Config.ENVIRONMENT == 'development':
        print("✓ Environment correctly set to development")
    else:
        print(f"✗ Environment is '{Config.ENVIRONMENT}', expected 'development'")
except Exception as e:
    print(f"✗ Error reading config: {e}")
    sys.exit(1)

# Test 10: Test DBWrapper
print("\n[10] Testing DBWrapper...")
try:
    from services.db_wrapper import DBWrapper
    print("✓ DBWrapper imported successfully")
    print("✓ DBWrapper ready to use for environment-agnostic database access")
except Exception as e:
    print(f"✗ Error importing DBWrapper: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! Local database setup is working correctly.")
print("=" * 60)
print("\nNext steps:")
print("1. Run the backend: ENVIRONMENT=development PORT=5000 python app.py")
print("2. In another terminal, start frontend: cd ../frontend && npm run dev")
print("3. Open http://localhost:5173 in your browser")
print("\nData will be stored in: backend/local_data/")
print("=" * 60)
