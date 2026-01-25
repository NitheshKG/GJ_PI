import os
import sys

# Debug: Print environment
print(f"DEBUG: SECRET_KEY={os.getenv('SECRET_KEY', 'NOT SET')}", file=sys.stderr)
print(f"DEBUG: FLASK_ENV={os.getenv('FLASK_ENV', 'NOT SET')}", file=sys.stderr)
print(f"DEBUG: PORT={os.getenv('PORT', 'NOT SET')}", file=sys.stderr)

from flask import Flask
from flask_cors import CORS
from config import Config
from services.db import init_db
from routes.tickets import tickets_bp
from routes.reports import reports_bp
from routes.close_ticket import close_ticket_bp
from routes.payments_api import payments_api_bp
from routes.customers import customers_bp
from routes.auth import auth_bp
from routes.alerts import alerts_bp

print(f"DEBUG: Config created, SECRET_KEY={Config.SECRET_KEY}", file=sys.stderr)

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS with allowed origins from config
CORS(app, resources={
    r"/api/*": {
        "origins": Config.CORS_ORIGINS,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "supports_credentials": True
    }
})

# Initialize DB
init_db(app)

# Register Blueprints
app.register_blueprint(tickets_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(close_ticket_bp)
app.register_blueprint(payments_api_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(alerts_bp)

@app.route('/')
def health_check():
    return {'status': 'healthy', 'service': 'Pawn Interest Backend'}

if __name__ == '__main__':
    # Get port from environment variable, default to 8080 for Cloud Run
    port = int(os.environ.get('PORT', 8080))
    # Use debug=False for production
    app.run(host='0.0.0.0', port=port, debug=False)
