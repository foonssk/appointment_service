from fastapi import FastAPI
from routes import appointments

app = FastAPI(title="Appointment Service")

app.include_router(appointments.router, prefix="/appointments")
