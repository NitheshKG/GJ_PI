from flask import Blueprint, request, jsonify
from services.db import get_db
from datetime import datetime

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customers_bp.route('', methods=['POST'])
def create_customer():
    """Create a new customer."""
    try:
        data = request.json
        db = get_db()

        # Check for duplicates
        phone = data.get('phone')
        if phone:
            existing_phone = list(db.collection('customers').where('phone', '==', phone).limit(1).stream())
            if existing_phone:
                return jsonify({'error': 'Customer with this phone number already exists'}), 400

        id_proof = data.get('idProofNumber')
        if id_proof:
            existing_id = list(db.collection('customers').where('idProofNumber', '==', id_proof).limit(1).stream())
            if existing_id:
                return jsonify({'error': 'Customer with this ID proof number already exists'}), 400

        name = data.get('name')
        if name:
            existing_name = list(db.collection('customers').where('name', '==', name).limit(1).stream())
            if existing_name:
                return jsonify({'error': 'Customer with this name already exists'}), 400
        
        customer_data = {
            'name': data.get('name'),
            'phone': data.get('phone'),
            'address': data.get('address'),
            'state': data.get('state'),
            'city': data.get('city'),
            'pincode': data.get('pincode'),
            'idProofType': data.get('idProofType', 'Aadhar'),
            'idProofOtherName': data.get('idProofOtherName'),
            'idProofNumber': data.get('idProofNumber'),
            'createdAt': datetime.now().isoformat()
        }
        
        customer_ref = db.collection('customers').document()
        customer_ref.set(customer_data)
        
        return jsonify({'id': customer_ref.id, 'message': 'Customer created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('', methods=['GET'])
def get_customers():
    """Get all customers with their ticket stats."""
    try:
        db = get_db()
        
        # Fetch all customers in a single query
        customers_ref = db.collection('customers')
        customers_docs = list(customers_ref.stream())
        
        # Fetch all tickets in a single query
        tickets_ref = db.collection('tickets')
        tickets_docs = list(tickets_ref.stream())
        
        # Build a map of customer stats from tickets
        customer_stats = {}
        for ticket_doc in tickets_docs:
            ticket = ticket_doc.to_dict()
            customer_id = ticket.get('customerId')
            if not customer_id:
                continue
            
            if customer_id not in customer_stats:
                customer_stats[customer_id] = {
                    'totalTickets': 0,
                    'activeTickets': 0,
                    'totalOutstanding': 0
                }
            
            # Count all tickets
            customer_stats[customer_id]['totalTickets'] += 1
            
            # Count only active tickets and their outstanding amounts
            if ticket.get('status') == 'Active':
                customer_stats[customer_id]['activeTickets'] += 1
                pending_principal = ticket.get('pendingPrincipal', 0)
                customer_stats[customer_id]['totalOutstanding'] += pending_principal

        customers = []
        for doc in customers_docs:
            customer = doc.to_dict()
            customer['id'] = doc.id
            
            # Use dynamically calculated stats from actual tickets
            stats = customer_stats.get(doc.id, {
                'totalTickets': 0,
                'activeTickets': 0,
                'totalOutstanding': 0
            })
            customer['totalTickets'] = stats['totalTickets']
            customer['activeTickets'] = stats['activeTickets']
            customer['totalOutstanding'] = stats['totalOutstanding']

            customers.append(customer)

        return jsonify(customers), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<customer_id>/tickets', methods=['GET'])
def get_customer_tickets(customer_id):
    """Get all tickets for a specific customer."""
    try:
        db = get_db()
        tickets_ref = db.collection('tickets')
        query = tickets_ref.where('customerId', '==', customer_id)
        docs = query.stream()
        
        tickets = []
        for doc in docs:
            ticket = doc.to_dict()
            ticket['id'] = doc.id
            
            # Use pre-stored values from ticket document
            ticket['totalInterestReceived'] = ticket.get('totalInterestReceived', 0)
            ticket['interestReceivedMonths'] = ticket.get('interestReceivedMonths', 0)
            
            tickets.append(ticket)
        
        # Sort tickets by lastPaymentDate (most recent first)
        tickets.sort(key=lambda t: t.get('lastPaymentDate') or '1970-01-01', reverse=True)
            
        return jsonify(tickets), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<customer_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_customer(customer_id):
    """Get, update, or delete a customer."""
    try:
        db = get_db()
        customer_ref = db.collection('customers').document(customer_id)
        customer_doc = customer_ref.get()
        
        if not customer_doc.exists:
            return jsonify({'error': 'Customer not found'}), 404
        
        # GET: Retrieve customer details
        if request.method == 'GET':
            customer = customer_doc.to_dict()
            customer['id'] = customer_doc.id
            return jsonify(customer), 200
        
        # PUT: Update customer details
        elif request.method == 'PUT':
            data = request.json
            
            # Fields to update
            update_data = {
                'name': data.get('name'),
                'phone': data.get('phone'),
                'address': data.get('address'),
                'state': data.get('state'),
                'city': data.get('city'),
                'pincode': data.get('pincode'),
                'idProofType': data.get('idProofType'),
                'idProofOtherName': data.get('idProofOtherName'),
                'idProofNumber': data.get('idProofNumber')
            }
            
            customer_ref.update(update_data)
            return jsonify({'message': 'Customer updated successfully'}), 200
        
        # DELETE: Delete customer and all associated tickets and payments
        elif request.method == 'DELETE':
            # Get all tickets for this customer
            tickets_query = db.collection('tickets').where('customerId', '==', customer_id)
            tickets_docs = list(tickets_query.stream())
            
            # Delete all payments associated with these tickets
            for ticket_doc in tickets_docs:
                ticket_id = ticket_doc.id
                payments_query = db.collection('payments').where('ticketId', '==', ticket_id)
                payments_docs = list(payments_query.stream())
                for payment_doc in payments_docs:
                    payment_id = payment_doc.id
                    payment_ref = db.collection('payments').document(payment_id)
                    payment_ref.delete()
            
            # Delete all tickets for this customer
            for ticket_doc in tickets_docs:
                ticket_id = ticket_doc.id
                ticket_ref = db.collection('tickets').document(ticket_id)
                ticket_ref.delete()
            
            # Delete the customer
            customer_ref.delete()
            
            return jsonify({'message': 'Customer deleted successfully along with all tickets and payments'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

