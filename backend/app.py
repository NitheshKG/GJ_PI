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

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

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
    app.run(debug=True, port=5000)
