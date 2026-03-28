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

@payments_api_bp.route('/payments/<payment_id>', methods=['PUT'])
def edit_payment(payment_id):
    """Edit a payment record"""
    try:
        data = request.json
        db = get_db()
        
        payment_ref = db.collection('payments').document(payment_id)
        payment_doc = payment_ref.get()
        
        if not payment_doc.exists:
            return jsonify({'error': 'Payment not found'}), 404
        
        payment_data = payment_doc.to_dict()
        
        # Build update data
        update_data = {}
        
        if 'interestPaid' in data:
            update_data['interestPaid'] = float(data.get('interestPaid', 0))
            if update_data['interestPaid'] > 0:
                update_data['interestReceivedAt'] = payment_data.get('interestReceivedAt')
        
        if 'principalPaid' in data:
            update_data['principalPaid'] = float(data.get('principalPaid', 0))
            if update_data['principalPaid'] > 0:
                update_data['principalReceivedAt'] = payment_data.get('principalReceivedAt')
        
        if 'monthsPaid' in data:
            update_data['monthsPaid'] = float(data.get('monthsPaid', 0))
        
        if 'date' in data:
            date_value = data.get('date')
            if not date_value:
                return jsonify({'error': 'Payment date is required'}), 400
            update_data['date'] = date_value
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Update the payment
        payment_ref.update(update_data)
        
        # Also update the ticket's totals if amounts changed
        ticket_id = payment_data.get('ticketId')
        if ticket_id and ('interestPaid' in data or 'principalPaid' in data or 'monthsPaid' in data):
            # Recalculate ticket totals by summing all payments for this ticket
            ticket_ref = db.collection('tickets').document(ticket_id)
            ticket_doc = ticket_ref.get()
            
            if ticket_doc.exists:
                ticket = ticket_doc.to_dict()
                
                # Get all payments for this ticket
                payments_query = db.collection('payments').where('ticketId', '==', ticket_id)
                all_payments = list(payments_query.stream())
                
                total_interest = 0
                total_months = 0
                total_principal_paid = 0
                
                for pay_doc in all_payments:
                    pay = pay_doc.to_dict()
                    total_interest += pay.get('interestPaid', 0)
                    total_months += pay.get('monthsPaid', 0)
                    total_principal_paid += pay.get('principalPaid', 0)
                
                # Update ticket with new totals
                original_principal = ticket.get('principal', 0)
                pending_principal = original_principal - total_principal_paid
                
                ticket_ref.update({
                    'totalInterestReceived': total_interest,
                    'interestReceivedMonths': total_months,
                    'pendingPrincipal': pending_principal
                })
        
        return jsonify({'message': 'Payment updated successfully'}), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_api_bp.route('/payments/<payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """Delete a payment record"""
    try:
        db = get_db()
        
        payment_ref = db.collection('payments').document(payment_id)
        payment_doc = payment_ref.get()
        
        if not payment_doc.exists:
            return jsonify({'error': 'Payment not found'}), 404
        
        payment_data = payment_doc.to_dict()
        ticket_id = payment_data.get('ticketId')
        
        # Delete the payment
        payment_ref.delete()
        
        # Recalculate ticket totals if it's linked to a ticket
        if ticket_id:
            ticket_ref = db.collection('tickets').document(ticket_id)
            ticket_doc = ticket_ref.get()
            
            if ticket_doc.exists:
                ticket = ticket_doc.to_dict()
                
                # Get all remaining payments for this ticket
                payments_query = db.collection('payments').where('ticketId', '==', ticket_id)
                all_payments = list(payments_query.stream())
                
                total_interest = 0
                total_months = 0
                total_principal_paid = 0
                
                for pay_doc in all_payments:
                    pay = pay_doc.to_dict()
                    total_interest += pay.get('interestPaid', 0)
                    total_months += pay.get('monthsPaid', 0)
                    total_principal_paid += pay.get('principalPaid', 0)
                
                # Update ticket with new totals
                original_principal = ticket.get('principal', 0)
                pending_principal = original_principal - total_principal_paid
                
                ticket_ref.update({
                    'totalInterestReceived': total_interest,
                    'interestReceivedMonths': total_months,
                    'pendingPrincipal': pending_principal
                })
        
        return jsonify({'message': 'Payment deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


