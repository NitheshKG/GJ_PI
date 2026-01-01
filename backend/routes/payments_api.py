from flask import Blueprint, request, jsonify
from services.db import get_db

payments_api_bp = Blueprint('payments_api', __name__, url_prefix='/api')

@payments_api_bp.route('/payments', methods=['GET'])
def get_all_payments():
    """Get all payments from the global payments collection."""
    try:
        db = get_db()
        payments_ref = db.collection('payments')
        docs = payments_ref.stream()
        
        payments = []
        for doc in docs:
            payment = doc.to_dict()
            payment['id'] = doc.id
            payments.append(payment)
            
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
