import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re
from waitress import serve

load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config.update(
    DEBUG=False,
    ENV='production'
)

# In-memory storage for bookings (in production, use database)
bookings = []

# Dashboard appointment cards content
DASHBOARD_APPOINTMENT_CARDS = [
    {
        'icon': '🩺',
        'title': 'General Checkup',
        'description': 'Routine health exams for preventive care and overall wellness.'
    },
    {
        'icon': '❤️',
        'title': 'Cardiac Screening',
        'description': 'Heart monitoring and ECG services to support cardiac health.'
    },
    {
        'icon': '🩸',
        'title': 'Diabetes Monitoring',
        'description': 'Diabetes management and follow-up appointments for consistent care.'
    },
    {
        'icon': '🚑',
        'title': 'Emergency Appointment',
        'description': 'Immediate care and urgent attention for critical medical needs.'
    },
    {
        'icon': '🔁',
        'title': 'Follow-up Appointment',
        'description': 'Post-treatment checks to monitor recovery and adjust care plans.'
    },
    {
        'icon': '🧪',
        'title': 'Diagnostic Appointment',
        'description': 'Testing and imaging services to identify health conditions accurately.'
    },
    {
        'icon': '💉',
        'title': 'Vaccination Appointment',
        'description': 'Immunizations for seasonal, travel, and booster vaccine needs.'
    },
    {
        'icon': '🏠',
        'title': 'Home Visit Appointment',
        'description': 'Care delivered at home for patients who need medical support on-site.'
    },
    {
        'icon': '💻',
        'title': 'Teleconsultation (Online)',
        'description': 'Remote consultations via video or phone for convenient care.'
    },
    {
        'icon': '🏥',
        'title': 'Surgery Appointment',
        'description': 'Planned surgical care with pre-op, operation, and post-op support.'
    }
]

# Email configuration from environment variables
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'False').lower() in ['true', '1', 'yes']
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', 'nadimpalliyoganandh@gmail.com')

def _is_placeholder_credential(value: str) -> bool:
    placeholder_keywords = [
        'your-email', 'your_email', 'your-app', 'your_password', 'your-password',
        'example.com', 'gmail.com'
    ]
    normalized = value.strip().lower()
    return not normalized or any(keyword in normalized for keyword in placeholder_keywords)

if EMAIL_ENABLED and (_is_placeholder_credential(SMTP_USERNAME) or _is_placeholder_credential(SMTP_PASSWORD)):
    print('WARNING: EMAIL_ENABLED is True but SMTP_USERNAME or SMTP_PASSWORD looks like a placeholder. Email will be disabled until valid credentials are provided.')
    EMAIL_ENABLED = False


def send_email(to_email, subject, body):
    """Send email notification"""
    if not EMAIL_ENABLED:
        print('Email sending skipped because EMAIL_ENABLED is False or credentials are invalid.')
        return False

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print('Email sending failed: SMTP_USERNAME and SMTP_PASSWORD must be set.')
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_email, text)
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print('Email sending failed: SMTP authentication error. Check your Gmail address and app password.')
        print(f'Error detail: {e}')
        return False
    except Exception as e:
        print(f'Email sending failed: {e}')
        return False


@app.route('/hybridaction/<path:action>', methods=['GET', 'POST'])
def hybridaction_handler(action):
    """Handle unwanted hybridaction tracker requests gracefully."""
    callback = request.args.get('__callback__') or request.args.get('callback')
    if callback:
        return Response(f"{callback}({{'status':'ok'}});", mimetype='application/javascript')
    return Response('{"status":"ok"}', mimetype='application/json')


def validate_mobile(mobile):
    """Validate mobile number (exactly 10 digits)"""
    return re.match(r'^\d{10}$', mobile) is not None

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - mobile number input"""
    if request.method == 'POST':
        mobile = request.form.get('mobile', '').strip()

        if not mobile:
            flash('Mobile number is required', 'error')
            return render_template('login.html')

        if not validate_mobile(mobile):
            flash('Mobile number must be exactly 10 digits', 'error')
            return render_template('login.html')

        # Store mobile in session and set logged in
        session['mobile'] = mobile
        session['logged_in'] = True

        # Send email notification
        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        email_body = f"""
        Ambulance Booking System - New Login

        Mobile Number: {mobile}
        Login Date & Time: {login_time}

        User has successfully logged in to the Ambulance Booking System.
        """

        send_email(NOTIFICATION_EMAIL, 'Ambulance Booking - New Login', email_body)

        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    mobile = session.get('mobile', 'Unknown')
    return render_template(
        'dashboard.html',
        mobile=mobile,
        active_page='home',
        appointment_cards=DASHBOARD_APPOINTMENT_CARDS,
        total_bookings=len(bookings)
    )

@app.route('/home')
def home():
    """Home page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    mobile = session.get('mobile', 'Unknown')
    total_bookings = len(bookings)
    return render_template('dashboard.html', mobile=mobile, active_page='home', total_bookings=total_bookings)

@app.route('/appointment_types')
def appointment_types():
    """Appointment types page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    mobile = session.get('mobile', 'Unknown')
    appointment_cards = [
        {
            'icon': '🩺',
            'title': 'General Consultation',
            'description': 'Basic check-up with a doctor for common health issues',
            'features': [
                'Physical examination',
                'Vital signs check',
                'Basic diagnostics',
                'Prescription',
                'Health advice'
            ]
        },
        {
            'icon': '👨‍⚕️',
            'title': 'Specialist Consultation',
            'description': 'Connect with a specialist for focused care',
            'features': [
                'Cardiologist',
                'Dermatologist',
                'Orthopedic',
                'Neurologist',
                'Gynecologist'
            ]
        },
        {
            'icon': '🚑',
            'title': 'Emergency Appointment',
            'description': 'Rapid response for urgent medical attention',
            'features': [
                'Immediate care',
                'Emergency room',
                'Critical care',
                'Rapid diagnostics',
                '24/7 response'
            ]
        },
        {
            'icon': '🔁',
            'title': 'Follow-up Appointment',
            'description': 'Continue care after your last visit',
            'features': [
                'Recovery tracking',
                'Medication update',
                'Test review',
                'Treatment adjustment'
            ]
        },
        {
            'icon': '🧪',
            'title': 'Diagnostic Appointment',
            'description': 'Advanced diagnostics to pinpoint your condition',
            'features': [
                'Blood tests',
                'X-ray / MRI',
                'Ultrasound',
                'ECG'
            ]
        },
        {
            'icon': '💉',
            'title': 'Vaccination Appointment',
            'description': 'Stay protected with timely vaccinations',
            'features': [
                'COVID-19',
                'Flu shots',
                'Travel vaccines',
                'Booster doses'
            ]
        },
        {
            'icon': '🏠',
            'title': 'Home Visit Appointment',
            'description': 'Medical care delivered to your home',
            'features': [
                'Doctor at home',
                'Mobile equipment',
                'Elder care'
            ]
        },
        {
            'icon': '💻',
            'title': 'Teleconsultation (Online)',
            'description': 'Remote care through phone or video',
            'features': [
                'Video call',
                'Phone consult',
                'Digital prescription'
            ]
        },
        {
            'icon': '🏥',
            'title': 'Surgery Appointment',
            'description': 'Care planning for surgical procedures',
            'features': [
                'Pre-op check',
                'Surgery planning',
                'Post-op care'
            ]
        }
    ]

    return render_template(
        'appointment_types.html',
        mobile=mobile,
        active_page='appointment_types',
        appointment_cards=appointment_cards
    )

@app.route('/logs')
def logs():
    """Logs page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    mobile = session.get('mobile', 'Unknown')
    return render_template('logs.html', mobile=mobile, active_page='logs', bookings=bookings)

@app.route('/book', methods=['GET', 'POST'])
def book():
    """Book ambulance page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        pickup_location = request.form.get('pickup_location', '').strip()
        hospital_location = request.form.get('hospital_location', '').strip()
        date = request.form.get('date', '').strip()
        appointment_type = request.form.get('appointment_type', '').strip()

        # Basic validation
        if not all([patient_name, mobile, pickup_location, hospital_location, date, appointment_type]):
            flash('All fields are required', 'error')
            return render_template('book.html')

        if not validate_mobile(mobile):
            flash('Mobile number must be exactly 10 digits', 'error')
            return render_template('book.html')

        # Save booking
        booking = {
            'id': len(bookings) + 1,
            'patient_name': patient_name,
            'mobile': mobile,
            'pickup_location': pickup_location,
            'hospital_location': hospital_location,
            'date': date,
            'appointment_type': appointment_type,
            'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        bookings.append(booking)

        flash(f'Booking successful! Booking ID: {booking["id"]}', 'success')
        return redirect(url_for('logs'))

    return render_template('book.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

if os.environ.get('FLASK_RUN_FROM_CLI'):
    raise RuntimeError('Please start this app with `python app.py` so it runs under Waitress, not Flask development server.')

if __name__ == '__main__':
    print('Starting Ambulance Booking app with Waitress...')
    print('Open http://127.0.0.1:5000 in your browser')
    print('Press CTRL+C to stop')
    serve(app, host='127.0.0.1', port=5000)