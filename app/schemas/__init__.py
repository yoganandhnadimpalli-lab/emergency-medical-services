from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class EmergencyRequestCreate(BaseModel):
    description: str
    location_lat: Optional[float]
    location_lng: Optional[float]
    priority: Optional[str] = 'medium'

class EmergencyRequestResponse(BaseModel):
    id: int
    user_id: int
    description: str
    location_lat: Optional[float]
    location_lng: Optional[float]
    status: str
    priority: str
    callback_time: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

class AppointmentCreate(BaseModel):
    appointment_date: datetime
    appointment_type: Optional[str] = 'monthly_checkup'
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    appointment_date: datetime
    appointment_type: str
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
