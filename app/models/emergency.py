from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class EmergencyRequest(Base):
    __tablename__ = 'emergency_requests'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(Text, nullable=False)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    status = Column(String(20), default='pending', nullable=False)
    priority = Column(String(20), default='medium', nullable=False)
    callback_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='emergency_requests')
