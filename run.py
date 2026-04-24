import os
import sys
from pathlib import Path
import uvicorn

print("🚨 Starting EMS FastAPI application...")
print("Visit: http://127.0.0.1:8000/docs for Swagger UI")

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

