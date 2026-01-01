from flask import Blueprint, request, jsonify, Response
from services.db import get_db
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import csv
from io import StringIO

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/monthly-interest', methods=['GET'])
def monthly_interest_report():
    """
    Get total interest received for a specific month.
    Query params:
    - month: YYYY-MM format (optional, defaults to current month)
    """
    try:
        db = get_db()
        
        # Get month parameter or use current month
        month_param = request.args.get('month')
        if month_param:
            target_date = datetime.strptime(month_param, '%Y-%m')
        else:
            target_date = datetime.now()
        
        # Calculate start and end of month
        start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = start_of_month + relativedelta(months=1)
        
        # Query global payments collection
        payments_ref = db.collection('payments')
        docs = payments_ref.stream()
        
        total_interest = 0
        total_principal = 0
        payment_count = 0
        payments_list = []
        
        for doc in docs:
            payment = doc.to_dict()
            payment_date = parser.isoparse(payment.get('date', ''))
            
            # Check if payment is in the target month
            if start_of_month <= payment_date < end_of_month:
                interest = payment.get('interestPaid', 0)
                principal = payment.get('principalPaid', 0)
                
                total_interest += interest
                total_principal += principal
                payment_count += 1
                
                payments_list.append({
                    'id': doc.id,
                    'date': payment.get('date'),
                    'customerName': payment.get('customerName'),
                    'interestPaid': interest,
                    'principalPaid': principal
                })
        
        return jsonify({
            'month': start_of_month.strftime('%Y-%m'),
            'totalInterest': total_interest,
            'totalPrincipal': total_principal,
            'paymentCount': payment_count,
            'payments': payments_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/outstanding-loans', methods=['GET'])
def outstanding_loans_report():
    """Get all tickets with outstanding principal."""
    try:
        db = get_db()
        tickets_ref = db.collection('tickets')
        docs = tickets_ref.stream()
        
        outstanding_tickets = []
        total_outstanding = 0
        
        for doc in docs:
            ticket = doc.to_dict()
            pending_principal = ticket.get('pendingPrincipal', 0)
            
            if pending_principal > 0:
                outstanding_tickets.append({
                    'id': doc.id,
                    'name': ticket.get('name'),
                    'articleName': ticket.get('articleName'),
                    'principal': ticket.get('principal'),
                    'pendingPrincipal': pending_principal,
                    'interestPercentage': ticket.get('interestPercentage'),
                    'startDate': ticket.get('startDate')
                })
                total_outstanding += pending_principal
        
        return jsonify({
            'totalOutstanding': total_outstanding,
            'tickets': outstanding_tickets
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/export/payment-report', methods=['GET'])
def export_payment_report():
    """
    Export payment report to CSV.
    Query params:
    - filterType: 'month', 'range', 'all' (required)
    - month: YYYY-MM format (required if filterType is 'month')
    - startMonth: YYYY-MM format (required if filterType is 'range')
    - endMonth: YYYY-MM format (required if filterType is 'range')
    """
    try:
        db = get_db()
        filter_type = request.args.get('filterType', 'month')
        
        # Get all payments and tickets
        payments_ref = db.collection('payments')
        all_payments = [{'id': doc.id, **doc.to_dict()} for doc in payments_ref.stream()]
        
        tickets_ref = db.collection('tickets')
        all_tickets = [{'id': doc.id, **doc.to_dict()} for doc in tickets_ref.stream()]
        
        # Filter based on type
        filtered_payments = []
        filtered_tickets = []
        
        if filter_type == 'all':
            filtered_payments = all_payments
            filtered_tickets = all_tickets
        elif filter_type == 'month':
            month_param = request.args.get('month')
            if not month_param:
                return jsonify({'error': 'month parameter is required for month filter'}), 400
            
            target_date = datetime.strptime(month_param, '%Y-%m')
            start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = start_of_month + relativedelta(months=1)
            
            filtered_payments = [
                p for p in all_payments 
                if start_of_month <= parser.isoparse(p.get('date', '')) < end_of_month
            ]
            filtered_tickets = [
                t for t in all_tickets
                if start_of_month <= parser.isoparse(t.get('startDate', '')) < end_of_month
            ]
        elif filter_type == 'range':
            start_month = request.args.get('startMonth')
            end_month = request.args.get('endMonth')
            
            if not start_month or not end_month:
                return jsonify({'error': 'startMonth and endMonth parameters are required for range filter'}), 400
            
            start_date = datetime.strptime(start_month, '%Y-%m')
            end_date = datetime.strptime(end_month, '%Y-%m')
            end_date = end_date + relativedelta(months=1)
            
            filtered_payments = [
                p for p in all_payments 
                if start_date <= parser.isoparse(p.get('date', '')) < end_date
            ]
            filtered_tickets = [
                t for t in all_tickets
                if start_date <= parser.isoparse(t.get('startDate', '')) < end_date
            ]
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Customer Name', 'Type', 'Interest Paid (₹)', 'Principal Amount (₹)'])
        
        # Combine tickets (investments) and payments into transactions
        transactions = []
        
        for ticket in filtered_tickets:
            transactions.append({
                'date': ticket.get('startDate', ''),
                'customerName': ticket.get('name', ''),
                'type': 'Invested',
                'interestPaid': 0,
                'principalPaid': ticket.get('principal', 0)
            })
        
        for payment in filtered_payments:
            transactions.append({
                'date': payment.get('date', ''),
                'customerName': payment.get('customerName', ''),
                'type': 'Received',
                'interestPaid': payment.get('interestPaid', 0),
                'principalPaid': payment.get('principalPaid', 0)
            })
        
        # Sort by date descending
        transactions.sort(key=lambda x: parser.isoparse(x['date']), reverse=True)
        
        # Write data rows
        for transaction in transactions:
            writer.writerow([
                datetime.fromisoformat(transaction['date'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S'),
                transaction['customerName'],
                transaction['type'],
                f"{transaction['interestPaid']:.2f}",
                f"{transaction['principalPaid']:.2f}"
            ])
        
        # Calculate totals
        total_interest = sum(t['interestPaid'] for t in transactions)
        total_principal_received = sum(t['principalPaid'] for t in transactions if t['type'] == 'Received')
        total_principal_invested = sum(t['principalPaid'] for t in transactions if t['type'] == 'Invested')
        
        # Add summary rows
        writer.writerow([])
        writer.writerow(['Summary'])
        writer.writerow(['Total Principal Invested', '', '', '', f"{total_principal_invested:.2f}"])
        writer.writerow(['Total Interest Received', '', '', f"{total_interest:.2f}", ''])
        writer.writerow(['Total Principal Received', '', '', '', f"{total_principal_received:.2f}"])
        writer.writerow(['Number of Transactions', '', len(transactions), '', ''])
        
        # Prepare response
        output.seek(0)
        filename = f"payment_report_{filter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/export/outstanding-loans', methods=['GET'])
def export_outstanding_loans():
    """Export outstanding loans report to CSV."""
    try:
        db = get_db()
        tickets_ref = db.collection('tickets')
        docs = tickets_ref.stream()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Ticket ID',
            'Customer Name',
            'Article Name',
            'Original Principal (₹)',
            'Pending Principal (₹)',
            'Interest Rate (%)',
            'Start Date',
            'Status'
        ])
        
        outstanding_tickets = []
        total_outstanding = 0
        
        for doc in docs:
            ticket = doc.to_dict()
            pending_principal = ticket.get('pendingPrincipal', 0)
            
            if pending_principal > 0:
                outstanding_tickets.append({
                    'id': doc.id,
                    'name': ticket.get('name', ''),
                    'articleName': ticket.get('articleName', ''),
                    'principal': ticket.get('principal', 0),
                    'pendingPrincipal': pending_principal,
                    'interestPercentage': ticket.get('interestPercentage', 0),
                    'startDate': ticket.get('startDate', ''),
                    'status': ticket.get('status', '')
                })
                total_outstanding += pending_principal
        
        # Sort by pending principal descending
        outstanding_tickets.sort(key=lambda x: x['pendingPrincipal'], reverse=True)
        
        # Write data rows
        for ticket in outstanding_tickets:
            writer.writerow([
                ticket['id'],
                ticket['name'],
                ticket['articleName'],
                f"{ticket['principal']:.2f}",
                f"{ticket['pendingPrincipal']:.2f}",
                f"{ticket['interestPercentage']:.2f}",
                datetime.fromisoformat(ticket['startDate'].replace('Z', '+00:00')).strftime('%Y-%m-%d'),
                ticket['status']
            ])
        
        # Add summary rows
        writer.writerow([])
        writer.writerow(['Summary'])
        writer.writerow(['Total Outstanding Principal', '', '', '', f"{total_outstanding:.2f}", '', '', ''])
        writer.writerow(['Number of Outstanding Tickets', '', len(outstanding_tickets), '', '', '', '', ''])
        
        # Prepare response
        output.seek(0)
        filename = f"outstanding_loans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
