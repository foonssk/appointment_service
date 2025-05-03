from datetime import datetime
from sqlalchemy.orm import Session
import redis
from dotenv import load_dotenv
import os
import httpx
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate

load_dotenv()

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)

# URL внутреннего API бота (внутри Docker сети)
BOT_API_URL = "http://bot-api:8001"  # Важно! Не localhost, а имя сервиса в docker-compose.yml

async def notify_bot(user_id: int, doctor_name: str, hospital: str, appointment_date: datetime):
    """Функция для отправки уведомления боту"""
    payload = {
        "user_id": user_id,
        "doctor": doctor_name,
        "hospital": hospital,
        "datetime": appointment_date.isoformat()
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BOT_API_URL}/notify", json=payload)
            if response.status_code != 200:
                print("Ошибка при отправке уведомления:", response.text)
        except Exception as e:
            print("Не удалось подключиться к боту:", str(e))

def create_appointment(db: Session, appointment: AppointmentCreate):
    slot_key = f"doctor:{appointment.doctor_id}:slot:{appointment.appointment_date}"
    
    # Проверяем, не занят ли слот
    if redis_client.get(slot_key):
        raise ValueError("This time slot is already booked")
    
    # Создаем запись в БД
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    # Помечаем слот как занятый
    redis_client.set(slot_key, "booked", ex=3600)

    # Получаем данные для уведомления
    try:
        doctor_name = db_appointment.doctor.name if db_appointment.doctor else "Врач"
        hospital = db_appointment.clinic.name if db_appointment.clinic else "Клиника"
    except Exception as e:
        doctor_name = "Врач"
        hospital = "Клиника"
        print("Ошибка получения данных о враче или клинике:", str(e))

    # Отправляем уведомление пользователю
    try:
        import asyncio
        asyncio.run(
            notify_bot(
                user_id=appointment.user_id,
                doctor_name=doctor_name,
                hospital=hospital,
                appointment_date=db_appointment.appointment_date
            )
        )
    except Exception as e:
        print("Ошибка при отправке уведомления боту:", str(e))

    return db_appointment