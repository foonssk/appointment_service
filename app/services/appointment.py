from datetime import datetime
from sqlalchemy.orm import Session
import redis
from dotenv import load_dotenv
import os
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
from app.telegram.bot import telegram_notifier

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)

def create_appointment(db: Session, appointment: AppointmentCreate):
    slot_key = f"doctor:{appointment.doctor_id}:slot:{appointment.appointment_date}"
    if redis_client.get(slot_key):
        raise ValueError("This time slot is already booked")
    
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    redis_client.set(slot_key, "booked", ex=3600)
    
    # Получаем дополнительную информацию о враче и больнице
    from app.models.doctor import Doctor
    from app.models.hospital import Hospital
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == doctor.hospital_id).first() if doctor else None
    
    # Отправляем уведомление в Telegram
    if doctor and hospital:
        appointment_info = {
            'hospital_name': hospital.name,
            'doctor_name': doctor.name,
            'appointment_date': appointment.appointment_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        telegram_notifier.schedule_reminder(appointment_info)
    
    return db_appointment

def get_appointment(db: Session, appointment_id: int):
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Appointment).offset(skip).limit(limit).all()