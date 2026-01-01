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
        docs = customers_ref.stream()

        customers = []
        for doc in docs:
            customer = doc.to_dict()
            customer['id'] = doc.id
            
            # Use pre-stored stats (will be updated via migration and on ticket creation/updates)
            customer['totalTickets'] = customer.get('totalTickets', 0)
            customer['activeTickets'] = customer.get('activeTickets', 0)
            customer['totalOutstanding'] = customer.get('totalOutstanding', 0)

            customers.append(customer)

        return jsonify(customers), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer details by ID."""
    try:
        db = get_db()
        customer_ref = db.collection('customers').document(customer_id)
        customer_doc = customer_ref.get()
        
        if not customer_doc.exists:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer = customer_doc.to_dict()
        customer['id'] = customer_doc.id
        
        return jsonify(customer), 200
        
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
            
        return jsonify(tickets), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@customers_bp.route('/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer details."""
    try:
        data = request.json
        db = get_db()
        customer_ref = db.collection('customers').document(customer_id)
        
        if not customer_ref.get().exists:
            return jsonify({'error': 'Customer not found'}), 404
            
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
        
        # Remove None values to avoid overwriting with null if field is missing in request (optional, but good practice)
        # However, for a full update form, we might want to allow clearing fields. 
        # Here we assume the frontend sends all current values.
        
        customer_ref.update(update_data)
        
        # Also update redundant data in tickets if any (optional but recommended for consistency)
        # This can be expensive if there are many tickets. For now, we update the customer.
        # Ideally, tickets should fetch customer details dynamically or use a denormalized update trigger.
        
        return jsonify({'message': 'Customer updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
