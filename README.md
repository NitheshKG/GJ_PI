# GJ_POS - Point of Sale System

A comprehensive Point of Sale (POS) system built with Vue.js frontend and Python Flask backend, designed to manage customers, tickets, payments, and reports.

## Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend build tool
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS** - Tool for transforming CSS with JavaScript

### Backend
- **Python** - Server-side language
- **Flask** - Lightweight web framework
- **SQLite/Database** - Data persistence

## Project Structure

```
GJ_PI/
├── frontend/                    # Vue.js frontend application
│   ├── src/
│   │   ├── components/         # Reusable Vue components
│   │   │   ├── ConfirmDialog.vue
│   │   │   └── ToastNotification.vue
│   │   ├── views/              # Page components
│   │   │   ├── Dashboard.vue
│   │   │   ├── NewTicket.vue
│   │   │   ├── Customers.vue
│   │   │   ├── CustomerDetails.vue
│   │   │   ├── RecordPayment.vue
│   │   │   ├── PaymentHistory.vue
│   │   │   └── Reports.vue
│   │   ├── stores/             # Pinia state management
│   │   │   ├── ticketStore.js
│   │   │   └── notificationStore.js
│   │   ├── router/             # Vue Router configuration
│   │   ├── App.vue             # Root component
│   │   ├── main.js             # Application entry point
│   │   └── style.css           # Global styles
│   ├── public/                 # Static assets
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   ├── postcss.config.js       # PostCSS configuration
│   ├── package.json            # Dependencies and scripts
│   └── index.html              # HTML entry point
│
└── backend/                     # Flask backend application
    ├── routes/                 # API endpoints
    │   ├── tickets.py          # Ticket management
    │   ├── customers.py        # Customer management
    │   ├── payments_api.py     # Payment processing
    │   ├── reports.py          # Reporting and analytics
    │   └── close_ticket.py     # Ticket closure operations
    ├── services/
    │   └── db.py               # Database service
    ├── app.py                  # Flask application entry point
    ├── config.py               # Configuration settings
    ├── requirements.txt        # Python dependencies
    └── migrations/             # Database migration scripts
        ├── migrate_customer_stats.py
        └── migrate_cache_customer_data.py
```

## Features

- **Ticket Management** - Create and manage sales tickets
- **Customer Management** - Maintain customer information and history
- **Payment Processing** - Record and track payments
- **Payment History** - View detailed payment records
- **Reports & Analytics** - Generate sales and customer reports
- **User-friendly Interface** - Responsive Vue.js frontend with Tailwind CSS styling
- **Notifications** - Real-time feedback with toast notifications
- **Confirmation Dialogs** - Secure operations with confirmation prompts

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations (if needed):
```bash
python migrate_customer_stats.py
python migrate_cache_customer_data.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Backend

From the `backend` directory:
```bash
python app.py
```

The API will be available at `http://localhost:5000` (or the configured port)

### Frontend

From the `frontend` directory:
```bash
npm run dev
```

The application will be available at `http://localhost:5173` (default Vite port)

## API Endpoints

### Tickets
- `GET /api/tickets` - Get all tickets
- `POST /api/tickets` - Create new ticket
- `PUT /api/tickets/<id>` - Update ticket
- `DELETE /api/tickets/<id>` - Delete ticket
- `POST /api/tickets/<id>/close` - Close ticket

### Customers
- `GET /api/customers` - Get all customers
- `POST /api/customers` - Create new customer
- `GET /api/customers/<id>` - Get customer details
- `PUT /api/customers/<id>` - Update customer

### Payments
- `POST /api/payments` - Record payment
- `GET /api/payments` - Get payment history
- `GET /api/payments/<id>` - Get payment details

### Reports
- `GET /api/reports/sales` - Sales report
- `GET /api/reports/customers` - Customer report

## Development

### Frontend Development
- Hot module replacement enabled for faster development
- Tailwind CSS for styling with responsive design
- Vue Router for client-side navigation

### Backend Development
- Flask development server with auto-reload
- Configuration management in `config.py`
- Database service abstraction in `services/db.py`

## Building for Production

### Frontend Build
```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

## License

This project is proprietary software.

## Support

For issues or questions, please contact the development team.
