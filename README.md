# Medical Appointment System

A complete full-stack Medical Appointment System built with FastAPI and Flask, featuring appointment scheduling, user authentication, and admin management.

## Features

- 🩺 **Medical Consultation System** - Schedule various types of medical appointments
- 📅 **Appointment Booking** - Book appointments for different medical services
- 🔐 **User Authentication** - Secure user registration and login
- 👨‍⚕️ **Multiple Consultation Types** - 10 different appointment categories
- 📱 **Emergency Support** - Direct emergency call functionality
- 🗄️ **MySQL Database** - Robust data storage with SQLAlchemy ORM
- 🌍 **Healthcare Services** - Comprehensive medical appointment management

## Recent Updates

- **Appointment Types Updated**: Changed from ambulance services to medical consultation types. Now offers 10 different appointment types including General Consultation, Specialist Consultation, Emergency Appointment, Follow-up, Diagnostic, Vaccination, Home Visit, Teleconsultation, Surgery, and Maternity appointments.
- **Emergency Call Button Added**: The emergency call button ("📱 9502567687") has been added back to the home page dashboard. Users can now click the emergency call button to directly call 9502567687 for immediate assistance.

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server

### One-Command Setup & Run
```bash
python run.py
```

This single command will:
1. Install all dependencies
2. Configure the environment
3. Run database migrations
4. Seed sample data
5. Start the FastAPI application
6. Display demo output

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Key Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Emergency Services
- `POST /api/emergency/` - Create emergency request
- `GET /api/emergency/{request_id}` - Get emergency request details
- `GET /api/emergency/` - List emergency requests (admin/patient)

### Appointments
- `POST /api/appointments/` - Book appointment
- `GET /api/appointments/` - List appointments

### Admin
- `GET /api/admin/users` - Manage users
- `PUT /api/admin/emergency/{request_id}/status` - Update emergency status

## Demo Output

The application will automatically demonstrate:
1. User registration and login
2. Emergency request creation with callback simulation
3. Appointment booking
4. Notification logs in console
5. Admin operations

## Project Structure

```
ems-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── emergency.py
│   │   └── appointment.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── emergency.py
│   │   └── appointment.py
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── emergency.py
│   │   ├── appointments.py
│   │   └── admin.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── notification.py
│   │   └── location.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── security.py
│       └── dependencies.py
├── alembic/                 # Database migrations
├── requirements.txt
├── .env                     # Environment variables
├── run.py                   # One-command runner
└── README.md
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- name
- phone
- hashed_password
- role (patient/admin)
- is_active
- created_at

### Emergency Requests Table
- id (Primary Key)
- user_id (Foreign Key)
- description
- location_lat, location_lng
- status (pending/dispatched/completed)
- priority (low/medium/high)
- callback_time
- created_at

### Appointments Table
- id (Primary Key)
- user_id (Foreign Key)
- appointment_date
- appointment_type
- status (scheduled/completed/cancelled)
- notes
- created_at

## Sample API Requests

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'
```

### Create Emergency Request
```bash
curl -X POST "http://localhost:8000/api/emergency/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Chest pain and difficulty breathing",
    "location_lat": 40.7128,
    "location_lng": -74.0060,
    "priority": "high"
  }'
```

### Book Appointment
```bash
curl -X POST "http://localhost:8000/api/appointments/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_date": "2024-01-15T10:00:00Z",
    "appointment_type": "monthly_checkup",
    "notes": "Regular health checkup"
  }'
```

## Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control (patient/admin)
- Input validation and sanitization
- CORS protection
- Rate limiting (configurable)

## Notification System

Notifications are simulated via console logs for demo purposes:
- SMS alerts for emergency callbacks
- Email confirmations for appointments
- Status updates for emergency requests

## Development

### Manual Setup (Alternative)
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed data
python -c "from app.database import seed_data; seed_data()"

# Start server
uvicorn app.main:app --reload
```

## Production Deployment

For production deployment:
1. Update `.env` with production credentials
2. Use a production ASGI server (e.g., Gunicorn + Uvicorn)
3. Configure reverse proxy (nginx)
4. Set up database backups
5. Enable HTTPS

## License

This project is for educational and demonstration purposes.