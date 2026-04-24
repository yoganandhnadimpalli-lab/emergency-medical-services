from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.routers.main import router as main_router

# import models for metadata
from app.models import User, EmergencyRequest, Appointment

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(main_router)

@app.get("/")
def root():
    return {"message": "EMS Service is running"}
