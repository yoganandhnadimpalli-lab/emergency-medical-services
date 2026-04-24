from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from typing import List

from app.schemas import UserCreate, UserLogin, UserResponse, Token, EmergencyRequestCreate, EmergencyRequestResponse, AppointmentCreate, AppointmentResponse
from app.database import get_db
from app.models import User, EmergencyRequest, Appointment
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.config import settings

router = APIRouter(prefix="/api")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None or 'sub' not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = db.query(User).filter(User.id == int(payload['sub'])).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


@router.post("/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=user_in.email,
        name=user_in.name,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        role='patient'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/emergency/", response_model=EmergencyRequestResponse)
def create_emergency(request_data: EmergencyRequestCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    callback_time = datetime.utcnow() + timedelta(minutes=5)
    new_request = EmergencyRequest(
        user_id=current_user.id,
        description=request_data.description,
        location_lat=request_data.location_lat,
        location_lng=request_data.location_lng,
        priority=request_data.priority,
        status='pending',
        callback_time=callback_time
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    print(f"[notification] Emergency request received for user {current_user.email}; callback at {callback_time.isoformat()} UTC")
    return new_request


@router.get("/emergency/", response_model=List[EmergencyRequestResponse])
def list_emergency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == 'admin':
        results = db.query(EmergencyRequest).all()
    else:
        results = db.query(EmergencyRequest).filter(EmergencyRequest.user_id == current_user.id).all()
    return results


@router.post("/appointments/", response_model=AppointmentResponse)
def book_appointment(appointment_data: AppointmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = Appointment(
        user_id=current_user.id,
        appointment_date=appointment_data.appointment_date,
        appointment_type=appointment_data.appointment_type,
        notes=appointment_data.notes,
        status='scheduled'
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    print(f"[notification] Appointment booked for {current_user.email} at {apt.appointment_date.isoformat()}")
    return apt


@router.get("/appointments/", response_model=List[AppointmentResponse])
def list_appointments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == 'admin':
        results = db.query(Appointment).all()
    else:
        results = db.query(Appointment).filter(Appointment.user_id == current_user.id).all()
    return results


@router.get("/admin/users", response_model=List[UserResponse])
def list_users(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return db.query(User).all()
