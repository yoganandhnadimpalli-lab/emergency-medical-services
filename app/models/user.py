from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default='patient')
    is_active = Column(String(5), default='true')
    created_at = Column(DateTime, default=datetime.utcnow)

    emergency_requests = relationship('EmergencyRequest', back_populates='user')
    appointments = relationship('Appointment', back_populates='user')
