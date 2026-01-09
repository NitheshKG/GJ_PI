from flask import Blueprint, request, jsonify
from services.db import get_db
from datetime import datetime

close_ticket_bp = Blueprint('close_ticket', __name__, url_prefix='/api/tickets')

@close_ticket_bp.route('/<ticket_id>/close', methods=['PUT'])
def close_ticket(ticket_id):
    """Close a ticket by setting status to 'Closed' and recording close date."""
    try:
        db = get_db()
        ticket_ref = db.collection('tickets').document(ticket_id)
        ticket_doc = ticket_ref.get()
        
        if not ticket_doc.exists:
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket_data = ticket_doc.to_dict()
        
        # Only close if ticket is currently active
        if ticket_data.get('status') != 'Active':
            return jsonify({'message': 'Ticket is already closed'}), 200
        
        # Update ticket status and close date
        ticket_ref.update({
            'status': 'Closed',
            'closeDate': datetime.now().isoformat()
        })
        
        # Update customer stats
        customer_id = ticket_data.get('customerId')
        if customer_id:
            customer_ref = db.collection('customers').document(customer_id)
            customer_doc = customer_ref.get()
            
            if customer_doc.exists:
                customer = customer_doc.to_dict()
                current_active_tickets = customer.get('activeTickets', 0)
                current_total_outstanding = customer.get('totalOutstanding', 0)
                pending_principal = ticket_data.get('pendingPrincipal', 0)
                
                # Decrease active tickets and outstanding amount
                customer_ref.update({
                    'activeTickets': max(0, current_active_tickets - 1),
                    'totalOutstanding': max(0, current_total_outstanding - pending_principal)
                })
        
        return jsonify({'message': 'Ticket closed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
