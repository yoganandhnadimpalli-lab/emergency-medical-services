import os

class Settings:
    database_url: str = os.environ.get('DATABASE_URL', 'mysql+mysqlconnector://root:password@localhost/ems_db')
    secret_key: str = os.environ.get('SECRET_KEY', 'your-super-secret-jwt-key-change-this-in-production')
    algorithm: str = os.environ.get('ALGORITHM', 'HS256')
    access_token_expire_minutes: int = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

    debug: bool = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    app_name: str = os.environ.get('APP_NAME', 'EMS Application')
    app_version: str = os.environ.get('APP_VERSION', '1.0.0')

    sms_enabled: bool = os.environ.get('SMS_ENABLED', 'False').lower() in ['true', '1', 'yes']
    email_enabled: bool = os.environ.get('EMAIL_ENABLED', 'False').lower() in ['true', '1', 'yes']

    twilio_account_sid: str = os.environ.get('TWILIO_ACCOUNT_SID', '')
    twilio_auth_token: str = os.environ.get('TWILIO_AUTH_TOKEN', '')
    twilio_phone_number: str = os.environ.get('TWILIO_PHONE_NUMBER', '')

    smtp_server: str = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username: str = os.environ.get('SMTP_USERNAME', '')
    smtp_password: str = os.environ.get('SMTP_PASSWORD', '')

settings = Settings()