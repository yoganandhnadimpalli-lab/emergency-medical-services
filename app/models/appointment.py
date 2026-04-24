from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    appointment_type = Column(String(50), default='monthly_checkup', nullable=False)
    status = Column(String(20), default='scheduled', nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='appointments')
