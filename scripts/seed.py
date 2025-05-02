from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.hospital import Hospital
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from datetime import date, time, datetime

engine = create_engine("postgresql://postgres:postgres@db:5432/appointment_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()

    # Добавляем больницу
    if not db.query(Hospital).filter_by(name="Central Hospital").first():
        hospital = Hospital(name="Central Hospital", address="Main St 1")
        db.add(hospital)
        db.commit()
        db.refresh(hospital)

    # Добавляем врача
    if not db.query(Doctor).filter_by(name="Dr. John Smith").first():
        doctor = Doctor(
            name="Dr. John Smith",
            hospital_id=1,
            work_day=date(2025, 4, 5),
            shift_start=time(9, 0),
            shift_end=time(17, 0)
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)

    # Добавляем запись
    if not db.query(Appointment).filter_by(patient_id=1001).first():
        appointment = Appointment(
            doctor_id=1,
            patient_id=1001,
            appointment_date=datetime(2025, 4, 5, 10, 0)
        )
        db.add(appointment)
        db.commit()

    print("✅ Seed data added successfully.")
    db.close()


if __name__ == "__main__":
    seed_data()
