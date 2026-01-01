"""
Migration script to cache customer data in ticket documents
for faster queries.
"""
from services.db import init_db
from flask import Flask

app = Flask(__name__)

# Initialize Firebase
init_app = init_db(app)
db = init_app

def migrate_cache_customer_data():
    """Add customer data to ticket documents."""
    print("Starting migration to cache customer data in tickets...")
    
    # Fetch all customers
    customers_ref = db.collection('customers')
    customers_dict = {}
    for customer_doc in customers_ref.stream():
        customers_dict[customer_doc.id] = customer_doc.to_dict()
    
    print(f"Found {len(customers_dict)} customers")
    
    # Fetch all tickets
    tickets_ref = db.collection('tickets')
    tickets = list(tickets_ref.stream())
    
    print(f"Found {len(tickets)} tickets")
    
    updated_count = 0
    
    for ticket_doc in tickets:
        ticket_data = ticket_doc.to_dict()
        customer_id = ticket_data.get('customerId')
        
        if customer_id and customer_id in customers_dict:
            customer = customers_dict[customer_id]
            
            # Update ticket with customer data
            ticket_doc.reference.update({
                'customerName': customer.get('name', ''),
                'customerPhone': customer.get('phone', ''),
                'customerAddress': customer.get('address', '')
            })
            
            print(f"Updated ticket {ticket_doc.id} with customer data from {customer.get('name')}")
            updated_count += 1
        else:
            print(f"Warning: Customer {customer_id} not found for ticket {ticket_doc.id}")
    
    print(f"\nMigration complete! Updated {updated_count} tickets with cached customer data.")

if __name__ == '__main__':
    try:
        migrate_cache_customer_data()
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
