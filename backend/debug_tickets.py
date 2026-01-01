"""
Debug script to check ticket data and date formats
"""
from services.db import init_db
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# Initialize Firebase
init_app = init_db(app)
db = init_app

def debug_tickets():
    """Check ticket data."""
    print("Debugging ticket data...")
    
    # Fetch all tickets
    tickets_ref = db.collection('tickets')
    tickets = list(tickets_ref.stream())
    
    print(f"\nFound {len(tickets)} tickets\n")
    
    current_date = datetime.now()
    print(f"Current date: {current_date}")
    print(f"Current year: {current_date.year}, month: {current_date.month}\n")
    
    for ticket_doc in tickets:
        ticket = ticket_doc.to_dict()
        ticket_id = ticket_doc.id
        
        print(f"Ticket ID: {ticket_id}")
        print(f"  Customer: {ticket.get('customerName')}")
        print(f"  Article: {ticket.get('articleName')}")
        print(f"  Start Date (raw): {ticket.get('startDate')}")
        print(f"  Start Date type: {type(ticket.get('startDate'))}")
        
        start_date_str = ticket.get('startDate')
        if start_date_str:
            try:
                # Try parsing as simple date
                if 'T' in start_date_str:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                    print(f"  Parsed as datetime: {start_date}")
                else:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    print(f"  Parsed as date: {start_date}")
                
                print(f"  Start year: {start_date.year}, month: {start_date.month}")
                months_diff = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
                print(f"  Months difference: {months_diff}")
            except Exception as e:
                print(f"  ERROR parsing date: {e}")
        
        print(f"  Interest Received Months: {ticket.get('interestReceivedMonths')}")
        print()

if __name__ == '__main__':
    try:
        debug_tickets()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
