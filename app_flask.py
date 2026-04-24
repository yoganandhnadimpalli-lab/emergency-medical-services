from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS
import os
from waitress import serve

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ems.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='patient')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmergencyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    callback_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('emergency_requests', lazy=True))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50), default='monthly_checkup')
    status = db.Column(db.String(20), default='scheduled')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

@app.route('/')
def root():
    return jsonify({'message': 'EMS Service is running. Use /health, /register, /login, /emergency, /appointments'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not all(k in data for k in ['name', 'email', 'phone', 'password']):
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=data['name'], email=data['email'], phone=data['phone'], password_hash=generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/hybridaction/<path:action>', methods=['GET', 'POST'])
def hybridaction_handler(action):
    """Handle unwanted hybridaction tracker requests gracefully."""
    callback = request.args.get('__callback__') or request.args.get('callback')
    if callback:
        return Response(f"{callback}({{'status':'ok'}});", mimetype='application/javascript')
    return Response('{"status":"ok"}', mimetype='application/json')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'role': user.role}})

@app.route('/emergency', methods=['POST'])
def emergency():
    data = request.json
    if not data or not data.get('user_id') or not data.get('description'):
        return jsonify({'error': 'Missing required fields'}), 400

    callback_time = datetime.utcnow() + timedelta(minutes=5)
    req = EmergencyRequest(user_id=data['user_id'], description=data['description'], location_lat=data.get('location_lat'), location_lng=data.get('location_lng'), priority=data.get('priority', 'medium'), callback_time=callback_time)
    db.session.add(req)
    db.session.commit()

    print(f"[notification] Emergency request {req.id} created; callback by {callback_time}")
    return jsonify({'message': 'Emergency request created', 'request_id': req.id, 'callback_time': callback_time.isoformat()}), 201

@app.route('/appointments', methods=['POST'])
def book_appointment():
    data = request.json
    if not data or not data.get('user_id') or not data.get('appointment_date'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        appointment_date = datetime.fromisoformat(data['appointment_date'])
    except Exception:
        return jsonify({'error': 'Invalid appointment_date format'}), 400

    apt = Appointment(user_id=data['user_id'], appointment_date=appointment_date, appointment_type=data.get('appointment_type', 'monthly_checkup'), notes=data.get('notes'))
    db.session.add(apt)
    db.session.commit()

    print(f"[notification] Appointment {apt.id} booked for user {apt.user_id} at {appointment_date}")
    return jsonify({'message': 'Appointment booked', 'appointment_id': apt.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    serve(app, host='127.0.0.1', port=5000)
