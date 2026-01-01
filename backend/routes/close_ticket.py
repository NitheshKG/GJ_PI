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
        
        # Update ticket status and close date
        ticket_ref.update({
            'status': 'Closed',
            'closeDate': datetime.now().isoformat()
        })
        
        return jsonify({'message': 'Ticket closed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
