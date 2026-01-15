from flask import Blueprint, request, jsonify
from services.db import get_db
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')

def calculate_completed_months(start_date, end_date):
    """
    Calculate the number of complete months between two dates, including fractional months.
    - 0-15 days = 0.5 months
    - 16+ days = 1.0 month added
    
    Example:
    - start: Nov 8, end: Nov 15 = 0.5 months (7 days)
    - start: Nov 8, end: Nov 24 = 1.0 month (16 days)
    - start: Nov 8, end: Dec 8 = 1.0 month (exactly 1 complete month)
    - start: Nov 8, end: Dec 15 = 1.5 months (1 month + 7 days)
    - start: Nov 8, end: Dec 24 = 2.0 months (1 month + 16 days)
    """
    # Calculate raw month difference
    months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # Track the fractional part
    fractional_months = 0.0
    
    # If we're in the same month, calculate based on days elapsed
    if start_date.year == end_date.year and start_date.month == end_date.month:
        days_elapsed = (end_date - start_date).days
        if days_elapsed > 0 and days_elapsed <= 15:
            fractional_months = 0.5
        elif days_elapsed > 15:
            fractional_months = 1.0
        return max(0, fractional_months)
    
    # If the day of end_date is less than day of start_date
    if end_date.day < start_date.day:
        # We haven't completed this month yet
        months_diff -= 1
        # Calculate fractional part based on days in current month
        days_into_month = end_date.day
        if days_into_month > 0 and days_into_month <= 15:
            fractional_months = 0.5
        elif days_into_month > 15:
            fractional_months = 1.0
    else:
        # We have completed this month
        # Calculate days into the current month (after the start day)
        days_into_month = end_date.day - start_date.day
        if days_into_month > 0 and days_into_month <= 15:
            fractional_months = 0.5
        elif days_into_month > 15:
            fractional_months = 1.0
    
    # Combine complete months with fractional months
    total_months = max(0, months_diff) + fractional_months
    return round(total_months, 1)  # Round to 1 decimal place

@tickets_bp.route('', methods=['POST'])
def create_ticket():
    try:
        data = request.json
        db = get_db()
        
        bill_number = data.get('billNumber', '')
        # Check if bill number is numeric
        if not str(bill_number).isdigit():
             return jsonify({'error': 'Bill number must contain only digits'}), 400
             
        # Check for duplicate bill number
        existing_bill = list(db.collection('tickets').where('billNumber', '==', bill_number).limit(1).stream())
        if existing_bill:
             return jsonify({'error': 'Ticket with this bill number already exists'}), 400
        
        principal = float(data.get('principal', 0))
        interest_percentage = float(data.get('interestPercentage', 0))
        customer_id = data.get('customerId')
        
        if not customer_id:
            return jsonify({'error': 'customerId is required'}), 400
        
        # Verify customer exists
        customer_ref = db.collection('customers').document(customer_id)
        if not customer_ref.get().exists:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get customer name for payment record
        customer = customer_ref.get().to_dict()
        customer_name = customer.get('name', 'Unknown')
        customer_phone = customer.get('phone', '')
        customer_address = customer.get('address', '')
        
        # Calculate first month interest and set dates
        first_month_interest = (principal * interest_percentage) / 100
        current_datetime = datetime.now().isoformat()
        start_date = data.get('startDate', current_datetime)
        
        # Use start date for the first month interest payment in reports
        # But use current datetime for lastPaymentDate so ticket appears at top of dashboard
        payment_date_for_report = start_date if start_date else current_datetime
        
        ticket_data = {
            'customerId': customer_id,
            'customerName': customer_name,
            'customerPhone': customer_phone,
            'customerAddress': customer_address,
            'billNumber': data.get('billNumber', ''),
            'articleName': data.get('articleName'),
            'itemType': data.get('itemType', 'Silver'),
            'grossWeight': float(data.get('grossWeight', 0)) if data.get('grossWeight') else None,
            'netWeight': float(data.get('netWeight', 0)) if data.get('netWeight') else None,
            'principal': principal,
            'pendingPrincipal': principal,
            'interestPercentage': interest_percentage,
            'startDate': start_date,
            'status': 'Active',
            'closeDate': None,
            'totalInterestReceived': first_month_interest,
            'interestReceivedMonths': 1,
            'lastPaymentDate': current_datetime,
            'createdAt': current_datetime
        }
        
        # Create ticket
        ticket_ref = db.collection('tickets').document()
        ticket_ref.set(ticket_data)
        ticket_id = ticket_ref.id
        
        # Create initial payment record for first month interest (received upfront)
        payment_data = {
            'ticketId': ticket_id,
            'customerName': customer_name,
            'date': payment_date_for_report,  # Use start date for correct monthly reporting
            'interestPaid': first_month_interest,
            'interestReceivedAt': payment_date_for_report,  # Use start date for reports
            'principalPaid': 0,
            'principalReceivedAt': None,
            'monthsPaid': 1,
            'remainingPrincipal': principal
        }
        
        # Add first month interest payment to global payments collection
        payment_ref = db.collection('payments').document()
        payment_ref.set(payment_data)
        
        # Update customer stats
        current_total_tickets = customer.get('totalTickets', 0)
        current_active_tickets = customer.get('activeTickets', 0)
        current_total_outstanding = customer.get('totalOutstanding', 0)
        
        customer_ref.update({
            'totalTickets': current_total_tickets + 1,
            'activeTickets': current_active_tickets + 1,
            'totalOutstanding': current_total_outstanding + principal
        })
        
        return jsonify({'id': ticket_id, 'message': 'Ticket created successfully with first month interest recorded'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('', methods=['GET'])
def get_tickets():
    try:
        db = get_db()
        
        # Fetch all tickets in one query
        tickets_ref = db.collection('tickets')
        tickets_docs = list(tickets_ref.stream())
        
        if not tickets_docs:
            return jsonify([]), 200
        
        tickets = []
        current_date = datetime.now()
        
        for doc in tickets_docs:
            ticket = doc.to_dict()
            ticket['id'] = doc.id
            
            # Customer details should already be cached in ticket document
            # If not present, they will be updated on next payment/create
            ticket['name'] = ticket.get('customerName', '')
            ticket['phone'] = ticket.get('customerPhone', '')
            ticket['address'] = ticket.get('customerAddress', '')
            
            # Use pre-stored values from ticket document
            ticket['totalInterestReceived'] = ticket.get('totalInterestReceived', 0)
            ticket['interestReceivedMonths'] = ticket.get('interestReceivedMonths', 0)
            
            # Calculate interest pending months (elapsed months since start date)
            start_date_str = ticket.get('startDate')
            if start_date_str:
                try:
                    # Handle both date (YYYY-MM-DD) and datetime (ISO format) strings
                    if 'T' in start_date_str:
                        # ISO datetime format
                        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                    else:
                        # Simple date format (YYYY-MM-DD)
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    
                    # Use the new calculation that considers the day component
                    completed_months = calculate_completed_months(start_date, current_date)
                    ticket['interestPendingMonths'] = completed_months
                except Exception as e:
                    print(f"Error parsing date {start_date_str}: {e}")
                    ticket['interestPendingMonths'] = 0
            else:
                ticket['interestPendingMonths'] = 0
            
            tickets.append(ticket)
        
        tickets.sort(key=lambda t: t.get('lastPaymentDate') or '1970-01-01', reverse=True)
            
        return jsonify(tickets), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        db = get_db()
        doc_ref = db.collection('tickets').document(ticket_id)
        doc = doc_ref.get()
        
        if doc.exists:
            ticket = doc.to_dict()
            ticket['id'] = doc.id
            
            # Calculate interest pending months (elapsed months since start date)
            current_date = datetime.now()
            start_date_str = ticket.get('startDate')
            if start_date_str:
                try:
                    # Handle both date (YYYY-MM-DD) and datetime (ISO format) strings
                    if 'T' in start_date_str:
                        # ISO datetime format
                        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                    else:
                        # Simple date format (YYYY-MM-DD)
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    
                    # Use the new calculation that considers the day component
                    completed_months = calculate_completed_months(start_date, current_date)
                    ticket['interestPendingMonths'] = completed_months
                except Exception as e:
                    print(f"Error parsing date {start_date_str}: {e}")
                    ticket['interestPendingMonths'] = 0
            else:
                ticket['interestPendingMonths'] = 0

            return jsonify(ticket), 200
        else:
            return jsonify({'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<ticket_id>/payments', methods=['POST'])
def add_payment(ticket_id):
    try:
        data = request.json
        db = get_db()
        
        ticket_ref = db.collection('tickets').document(ticket_id)
        ticket_doc = ticket_ref.get()
        
        if not ticket_doc.exists:
            return jsonify({'error': 'Ticket not found'}), 404
            
        ticket_data = ticket_doc.to_dict()
        current_pending_principal = ticket_data.get('pendingPrincipal', ticket_data.get('principal'))
        
        interest_paid = float(data.get('interestPaid', 0))
        principal_paid = float(data.get('principalPaid', 0))
        months_paid = int(data.get('monthsPaid', 0))
        
        new_pending_principal = current_pending_principal - principal_paid
        
        # Current timestamp
        current_datetime = datetime.now().isoformat()
        
        # Get customer name from customer document
        customer_id = ticket_data.get('customerId')
        customer_name = 'Unknown'
        if customer_id:
            customer_ref = db.collection('customers').document(customer_id)
            customer_doc = customer_ref.get()
            if customer_doc.exists:
                customer_name = customer_doc.to_dict().get('name', 'Unknown')
        
        payment_data = {
            'ticketId': ticket_id,  # Link to ticket
            'customerName': customer_name,  # Fetch from customer record
            'date': current_datetime,  # General payment date
            'interestPaid': interest_paid,
            'interestReceivedAt': current_datetime if interest_paid > 0 else None,
            'principalPaid': principal_paid,
            'principalReceivedAt': current_datetime if principal_paid > 0 else None,
            'monthsPaid': months_paid,
            'remainingPrincipal': new_pending_principal
        }
        
        # Add payment record to GLOBAL payments collection
        payment_ref = db.collection('payments').document()
        payment_ref.set(payment_data)
        
        # Calculate new totals for ticket
        current_total_interest = ticket_data.get('totalInterestReceived', 0)
        current_total_months = ticket_data.get('interestReceivedMonths', 0)
        
        # Update ticket with new values
        ticket_ref.update({
            'pendingPrincipal': new_pending_principal,
            'totalInterestReceived': current_total_interest + interest_paid,
            'interestReceivedMonths': current_total_months + months_paid,
            'lastPaymentDate': current_datetime
        })
        
        return jsonify({'message': 'Payment recorded successfully', 'newPendingPrincipal': new_pending_principal}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tickets_bp.route('/<ticket_id>/payments', methods=['GET'])
def get_payments(ticket_id):
    try:
        db = get_db()
        # Query global payments collection filtered by ticketId using where clause
        payments_ref = db.collection('payments')
        query = payments_ref.where('ticketId', '==', ticket_id)
        docs = query.stream()
        
        payments = []
        for doc in docs:
            payment = doc.to_dict()
            payment['id'] = doc.id
            payments.append(payment)
            
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
