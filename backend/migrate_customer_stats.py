"""
Migration script to cache ticket stats in customer documents
for faster queries.
"""
from services.db import init_db
from flask import Flask

app = Flask(__name__)

# Initialize Firebase
init_app = init_db(app)
db = init_app

def migrate_cache_customer_stats():
    """Add ticket stats to customer documents."""
    print("Starting migration to cache customer stats...")
    
    # Fetch all tickets
    tickets_ref = db.collection('tickets')
    all_tickets = list(tickets_ref.stream())
    
    print(f"Found {len(all_tickets)} tickets")
    
    # Group tickets by customerId
    tickets_by_customer = {}
    for ticket_doc in all_tickets:
        ticket = ticket_doc.to_dict()
        customer_id = ticket.get('customerId')
        if customer_id:
            if customer_id not in tickets_by_customer:
                tickets_by_customer[customer_id] = []
            tickets_by_customer[customer_id].append(ticket)
    
    # Fetch all customers
    customers_ref = db.collection('customers')
    customers = list(customers_ref.stream())
    
    print(f"Found {len(customers)} customers")
    
    updated_count = 0
    
    for customer_doc in customers:
        customer_id = customer_doc.id
        customer_tickets = tickets_by_customer.get(customer_id, [])
        
        # Calculate stats
        total_tickets = len(customer_tickets)
        active_tickets = sum(1 for t in customer_tickets if t.get('status') == 'Active')
        total_outstanding = sum(t.get('pendingPrincipal', 0) for t in customer_tickets if t.get('status') == 'Active')
        
        # Update customer with stats
        customer_doc.reference.update({
            'totalTickets': total_tickets,
            'activeTickets': active_tickets,
            'totalOutstanding': total_outstanding
        })
        
        print(f"Updated customer {customer_doc.id}: {total_tickets} tickets, {active_tickets} active, ₹{total_outstanding} outstanding")
        updated_count += 1
    
    print(f"\nMigration complete! Updated {updated_count} customers with cached stats.")

if __name__ == '__main__':
    try:
        migrate_cache_customer_stats()
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
