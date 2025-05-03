from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.base import SessionLocal
from app.telegram.bot import telegram_notifier  # Правильный путь

# Импорты для больниц
from app.services import hospital as hospital_service
from app.schemas import Hospital, HospitalCreate

# Импорты для докторов
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, Doctor as DoctorSchema
from app.services.doctor import create_doctor, get_doctors, get_doctor

# Импорты для записей
from app.services import appointment as appointment_service
from app.schemas import Appointment, AppointmentCreate

from app.models.base import SessionLocal

app = FastAPI(
    title="Appointment Microservice API",
    description="API для управления больницами, врачами и записями на приём",
    version="1.0.0",
    contact={
        "name": "Ваше имя",
        "email": "ваш.email@example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Hospitals",
            "description": "Операции с больницами",
        },
        {
            "name": "Doctors",
            "description": "Операции с врачами",
        },
        {
            "name": "Appointments",
            "description": "Операции с записями на приём",
        },
        {
            "name": "Health Check",
            "description": "Проверка работоспособности сервиса",
        },
    ]
)

@app.on_event("startup")
async def startup_event():
    telegram_notifier.start()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинты для больниц
@app.post(
    "/hospitals/",
    response_model=Hospital,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую больницу",
    tags=["Hospitals"],
    responses={
        201: {"description": "Больница успешно создана"},
        400: {"description": "Неверные входные данные"}
    }
)
def create_hospital(hospital: HospitalCreate, db: Session = Depends(get_db)):
    """
    Создать новую больницу в системе.
    
    - **name**: Название больницы (обязательное поле)
    - **address**: Физический адрес больницы (обязательное поле)
    """
    return hospital_service.create_hospital(db=db, hospital=hospital)

@app.get(
    "/hospitals/",
    response_model=List[Hospital],
    summary="Получить список больниц",
    tags=["Hospitals"],
    responses={
        200: {"description": "Список больниц успешно получен"}
    }
)
def read_hospitals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить список всех больниц с возможностью пагинации.
    
    - **skip**: Количество пропускаемых записей (по умолчанию 0)
    - **limit**: Максимальное количество возвращаемых записей (по умолчанию 100)
    """
    return hospital_service.get_hospitals(db=db, skip=skip, limit=limit)

# Эндпоинты для докторов
@app.post(
    "/doctors/",
    response_model=DoctorSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить нового врача",
    tags=["Doctors"],
    responses={
        201: {"description": "Врач успешно добавлен"},
        400: {"description": "Неверные входные данные"},
        404: {"description": "Больница не найдена"}
    }
)
def add_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """
    Добавить нового врача в систему.
    
    - **name**: ФИО врача
    - **hospital_id**: ID больницы
    - **work_days**: Дни работы (например, ["mon", "wed", "fri"])
    - **shift_start**: Начало смены (формат HH:MM)
    - **shift_end**: Конец смены (формат HH:MM)
    """
    return create_doctor(db=db, doctor=doctor)

@app.get(
    "/doctors/",
    response_model=List[DoctorSchema],
    summary="Получить список врачей",
    tags=["Doctors"],
    responses={
        200: {"description": "Список врачей успешно получен"}
    }
)
def list_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить список всех врачей с возможностью пагинации.
    
    - **skip**: Количество пропускаемых записей (по умолчанию 0)
    - **limit**: Максимальное количество возвращаемых записей (по умолчанию 100)
    """
    return get_doctors(db=db, skip=skip, limit=limit)

@app.get(
    "/doctors/{doctor_id}",
    response_model=DoctorSchema,
    summary="Получить информацию о враче",
    tags=["Doctors"],
    responses={
        200: {"description": "Информация о враче получена"},
        404: {"description": "Врач не найден"}
    }
)
def get_doctor_info(doctor_id: int, db: Session = Depends(get_db)):
    """
    Получить подробную информацию о конкретном враче по его ID.
    
    - **doctor_id**: ID врача
    """
    doctor = get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    return doctor

# Эндпоинты для записей на приём
@app.post(
    "/appointments/",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запись на приём",
    tags=["Appointments"],
    responses={
        201: {"description": "Запись успешно создана"},
        400: {"description": "Неверные входные данные или слот занят"},
        404: {"description": "Врач или пациент не найден"}
    }
)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Создать новую запись на приём к врачу.
    
    - **doctor_id**: ID врача
    - **patient_id**: ID пациента
    - **appointment_date**: Дата и время приёма (в формате YYYY-MM-DD HH:MM:SS)
    """
    try:
        return appointment_service.create_appointment(db=db, appointment=appointment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get(
    "/appointments/",
    response_model=List[Appointment],
    summary="Получить список записей",
    tags=["Appointments"],
    responses={
        200: {"description": "Список записей успешно получен"}
    }
)
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить список всех записей на приём с возможностью пагинации.
    
    - **skip**: Количество пропускаемых записей (по умолчанию 0)
    - **limit**: Максимальное количество возвращаемых записей (по умолчанию 100)
    """
    return appointment_service.get_appointments(db=db, skip=skip, limit=limit)

# Health check
@app.get(
    "/health",
    summary="Проверить статус сервиса",
    tags=["Health Check"],
    responses={
        200: {"description": "Сервис работает корректно"}
    }
)
def health_check():
    """
    Проверить работоспособность сервиса.
    
    Возвращает статус работы сервиса.
    """
    return {"status": "OK"}