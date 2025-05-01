from fastapi import APIRouter, HTTPException
from models import Appointment
from typing import List
from datetime import datetime

router = APIRouter()

# Временное хранилище записей
fake_db: List[Appointment] = []

@router.get("/", response_model=List[Appointment])
def get_appointments():
    return fake_db

@router.post("/", response_model=Appointment)
def create_appointment(appointment: Appointment):
    # Проверка на дубликат
    for a in fake_db:
        if a.id == appointment.id:
            raise HTTPException(status_code=400, detail="Appointment with this ID already exists.")
    fake_db.append(appointment)
    return appointment

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int):
    global fake_db
    fake_db = [a for a in fake_db if a.id != appointment_id]
    return {"message": "Deleted"}
