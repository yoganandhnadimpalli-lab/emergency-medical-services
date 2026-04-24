#!/usr/bin/env python
"""Test script to verify admin user and test login"""

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Initialize database context
with app.app_context():
    # Create tables
    db.create_all()
    
    print("Checking for existing admin user...")
    admin = User.query.filter_by(email='admin@ems.com').first()
    
    if admin:
        print(f"✓ Admin user found: ID={admin.id}, Name={admin.name}")
        print(f"  Email: {admin.email}")
        print(f"  Role: {admin.role}")
    else:
        print("✗ Admin user not found, creating...")
        new_admin = User(
            name='EMS Admin',
            email='admin@ems.com',
            phone='+1234567890',
            role='admin'
        )
        new_admin.password_hash = generate_password_hash('admin123')
        db.session.add(new_admin)
        db.session.commit()
        print("✓ Admin user created successfully")
    
    print("\nTesting password verification...")
    admin = User.query.filter_by(email='admin@ems.com').first()
    
    # Test the password
    test_password = 'admin123'
    is_valid = check_password_hash(admin.password_hash, test_password)
    print(f"Password 'admin123' is valid: {is_valid}")
    
    if is_valid:
        print("✓ Password verification works correctly")
    else:
        print("✗ Password verification failed!")
        print(f"  Stored hash: {admin.password_hash[:30]}...")
    
    print("\nTesting login via API...")
    
    # Test via client
    client = app.test_client()
    
    login_data = {
        'email': 'admin@ems.com',
        'password': 'admin123'
    }
    
    response = client.post('/api/login', 
                          json=login_data,
                          content_type='application/json')
    
    print(f"Response status: {response.status_code}")
    response_data = json.loads(response.data)
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if response.status_code == 200:
        print("✓ Login successful!")
    else:
        print("✗ Login failed!")
