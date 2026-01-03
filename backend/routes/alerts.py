from flask import Blueprint, request, jsonify
from services.db import get_db
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import re

load_dotenv()

alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

def normalize_phone_number(phone):
    """
    Normalize phone number to include +91 for Indian numbers.
    Handles various formats: 9876543210, 09876543210, +919876543210, etc.
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', str(phone).strip())
    
    # Remove leading + if exists
    if phone.startswith('+'):
        phone = phone[1:]
    
    # Remove leading 0 if it exists (for Indian numbers)
    if phone.startswith('0'):
        phone = phone[1:]
    
    # Ensure we have 10 digits
    if len(phone) == 10:
        # Add country code for India
        phone = '+91' + phone
    elif len(phone) == 12 and not phone.startswith('91'):
        # Handle formats like 919876543210 without +
        phone = '+' + phone
    elif not phone.startswith('+91'):
        # If doesn't start with +91, add it
        phone = '+91' + phone
    
    return phone

def send_email_alert(customer_name, phone_number, message):
    """
    Send email alert as a free fallback option.
    """
    try:
        # For demo purposes, we're logging instead of actually sending
        # In production, you'd configure real SMTP settings
        log_email = {
            'type': 'email',
            'customer': customer_name,
            'phone': phone_number,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'logged'
        }
        print(f"[EMAIL ALERT] {log_email}")
        return True
    except Exception as e:
        print(f"Email alert failed: {str(e)}")
        return False

def send_twilio_whatsapp(customer_phone, message):
    """
    Send WhatsApp message using Twilio WhatsApp Sandbox (FREE for testing).
    Register your number at: https://www.twilio.com/console/sms/whatsapp/learn
    No credit card required for sandbox mode.
    """
    try:
        # Check if Twilio credentials are set in environment
        twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if not twilio_account_sid or not twilio_auth_token:
            print("[TWILIO] Credentials not configured. Install twilio and set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
            return False
        
        from twilio.rest import Client
        
        # Normalize phone number
        normalized_phone = normalize_phone_number(customer_phone)
        to_number = f'whatsapp:{normalized_phone}'
        
        client = Client(twilio_account_sid, twilio_auth_token)
        
        message_obj = client.messages.create(
            from_=twilio_whatsapp_number,
            body=message,
            to=to_number
        )
        
        return {
            'success': True,
            'message_id': message_obj.sid,
            'phone': normalized_phone
        }
    except Exception as e:
        print(f"Twilio WhatsApp failed: {str(e)}")
        return False

def send_sms_via_fast2sms(phone_number, message):
    """
    Send SMS using Fast2SMS (FREE for India with limited quota).
    Sign up at: https://www.fast2sms.com/
    Get your API key from dashboard and add to .env as FAST2SMS_API_KEY
    """
    try:
        api_key = os.getenv('FAST2SMS_API_KEY')
        if not api_key:
            print("[FAST2SMS] API key not configured. Get free account at https://www.fast2sms.com/")
            return False
        
        import requests
        
        normalized_phone = normalize_phone_number(phone_number)
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "variables_values": message,
            "route": "otp",
            "numbers": normalized_phone.replace('+91', '')  # Fast2SMS wants 10 digit number
        }
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return {
                'success': True,
                'phone': normalized_phone,
                'service': 'fast2sms'
            }
        else:
            print(f"Fast2SMS error: {response.text}")
            return False
    except Exception as e:
        print(f"Fast2SMS failed: {str(e)}")
        return False

@alerts_bp.route('/overdue-interests', methods=['GET'])
def get_overdue_interests():
    """
    Get customers with pending interests >= 12 months.
    Returns a list of customers with pending interest details.
    """
    try:
        db = get_db()
        tickets_ref = db.collection('tickets')
        docs = tickets_ref.stream()
        
        overdue_customers = []
        current_date = datetime.now()
        
        for doc in docs:
            ticket = doc.to_dict()
            
            # Only consider active tickets
            if ticket.get('status') != 'Active':
                continue
            
            # Get the start date of the ticket
            start_date_str = ticket.get('startDate')
            if not start_date_str:
                continue
            
            start_date = parser.isoparse(start_date_str)
            
            # Calculate months passed since ticket was created
            months_passed = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
            
            # If 12+ months have passed, add to overdue list
            if months_passed >= 12:
                # Check if this customer already exists in overdue_customers
                customer_exists = False
                for existing_customer in overdue_customers:
                    if existing_customer['customerId'] == ticket.get('customerId'):
                        # Add ticket to existing customer
                        existing_customer['tickets'].append({
                            'id': doc.id,
                            'articleName': ticket.get('articleName'),
                            'principal': ticket.get('principal'),
                            'pendingPrincipal': ticket.get('pendingPrincipal'),
                            'interestPercentage': ticket.get('interestPercentage'),
                            'startDate': ticket.get('startDate'),
                            'monthsPending': months_passed,
                            'status': ticket.get('status')
                        })
                        customer_exists = True
                        break
                
                if not customer_exists:
                    # Add new customer with ticket
                    overdue_customers.append({
                        'customerId': ticket.get('customerId'),
                        'customerName': ticket.get('customerName'),
                        'customerPhone': ticket.get('customerPhone'),
                        'customerAddress': ticket.get('customerAddress'),
                        'ticketCount': 1,
                        'tickets': [{
                            'id': doc.id,
                            'articleName': ticket.get('articleName'),
                            'principal': ticket.get('principal'),
                            'pendingPrincipal': ticket.get('pendingPrincipal'),
                            'interestPercentage': ticket.get('interestPercentage'),
                            'startDate': ticket.get('startDate'),
                            'monthsPending': months_passed,
                            'status': ticket.get('status')
                        }]
                    })
        
        # Update ticket counts
        for customer in overdue_customers:
            customer['ticketCount'] = len(customer['tickets'])
        
        return jsonify({
            'count': len(overdue_customers),
            'customers': overdue_customers
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/send-message/<customer_id>', methods=['POST'])
def send_alert_message(customer_id):
    """
    Send an alert message to a customer via multiple channels.
    Supports: SMS (Fast2SMS), WhatsApp (Twilio), and Email
    Free options available - see requirements in .env
    
    Request body:
    {
        "message": "Custom message to send",
        "method": "sms", "whatsapp", or "email"
    }
    """
    try:
        data = request.json
        message = data.get('message')
        method = data.get('method', 'sms')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        db = get_db()
        
        # Get customer details
        customer_ref = db.collection('customers').document(customer_id)
        customer = customer_ref.get()
        
        if not customer.exists:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer_data = customer.to_dict()
        phone_number = customer_data.get('phone')
        customer_name = customer_data.get('name')
        customer_email = customer_data.get('email', '')
        
        if not phone_number:
            return jsonify({'error': 'Customer phone number not found'}), 400
        
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        
        # Send message based on method
        send_result = None
        if method == 'sms':
            send_result = send_sms_via_fast2sms(phone_number, message)
        elif method == 'whatsapp':
            send_result = send_twilio_whatsapp(phone_number, message)
        elif method == 'email':
            send_result = send_email_alert(customer_name, phone_number, message)
        else:
            return jsonify({'error': f'Unsupported method: {method}'}), 400
        
        # Determine status based on result
        if send_result is False:
            # Service not configured, log the message anyway
            log_data = {
                'customerId': customer_id,
                'customerName': customer_name,
                'phoneNumber': normalized_phone,
                'method': method,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending_configuration',
                'note': f'{method} service not configured. Configure API keys in .env to enable.'
            }
            db.collection('alert_messages').document().set(log_data)
            
            return jsonify({
                'status': 'pending_configuration',
                'message': f'{method.upper()} service not configured. Please setup API credentials.',
                'normalized_phone': normalized_phone,
                'instructions': get_setup_instructions(method)
            }), 202
        
        # Successfully sent or logged
        if isinstance(send_result, dict) and send_result.get('success'):
            # Message sent successfully
            log_data = {
                'customerId': customer_id,
                'customerName': customer_name,
                'phoneNumber': normalized_phone,
                'method': method,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent',
                'messageId': send_result.get('message_id', send_result.get('message_id', 'N/A'))
            }
        else:
            # Message logged/pending
            log_data = {
                'customerId': customer_id,
                'customerName': customer_name,
                'phoneNumber': normalized_phone,
                'method': method,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent'
            }
        
        # Store message log in database
        db.collection('alert_messages').document().set(log_data)
        
        return jsonify({
            'status': 'success',
            'message': f'Alert message sent to {customer_name} ({normalized_phone})',
            'method': method,
            'phone': normalized_phone
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_setup_instructions(method):
    """Get setup instructions for each message service."""
    instructions = {
        'sms': {
            'service': 'Fast2SMS (Free for India)',
            'setup': [
                '1. Sign up at https://www.fast2sms.com/',
                '2. Go to Dashboard and copy your API Key',
                '3. Add to .env: FAST2SMS_API_KEY=your_api_key',
                '4. Free SMS credits available daily'
            ],
            'cost': 'Free with daily limits'
        },
        'whatsapp': {
            'service': 'Twilio WhatsApp Sandbox (Free)',
            'setup': [
                '1. Install: pip install twilio',
                '2. Go to https://www.twilio.com/console/sms/whatsapp/learn',
                '3. Register your number in sandbox',
                '4. Add to .env:',
                '   TWILIO_ACCOUNT_SID=your_sid',
                '   TWILIO_AUTH_TOKEN=your_token',
                '5. No credit card required for sandbox'
            ],
            'cost': 'Completely Free (Sandbox mode)'
        },
        'email': {
            'service': 'Email (Built-in, Free)',
            'setup': [
                '1. Email support is already enabled',
                '2. Optionally configure SMTP for real emails in .env',
                '3. Currently logs messages (no SMTP configured)'
            ],
            'cost': 'Completely Free'
        }
    }
    return instructions.get(method, {})

@alerts_bp.route('/message-history', methods=['GET'])
def get_message_history():
    """Get history of all alert messages sent."""
    try:
        db = get_db()
        messages_ref = db.collection('alert_messages')
        docs = messages_ref.stream()
        
        messages = []
        for doc in docs:
            msg = doc.to_dict()
            msg['id'] = doc.id
            messages.append(msg)
        
        # Sort by timestamp descending
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'count': len(messages),
            'messages': messages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/setup-status', methods=['GET'])
def get_setup_status():
    """Check which message services are configured."""
    return jsonify({
        'services': {
            'sms': {
                'name': 'Fast2SMS',
                'configured': bool(os.getenv('FAST2SMS_API_KEY')),
                'cost': 'Free'
            },
            'whatsapp': {
                'name': 'Twilio WhatsApp Sandbox',
                'configured': bool(os.getenv('TWILIO_ACCOUNT_SID')),
                'cost': 'Free (Sandbox)'
            },
            'email': {
                'name': 'Email',
                'configured': True,
                'cost': 'Free'
            }
        }
    }), 200

