from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.services import hospital as hospital_service
from app.schemas import Hospital, HospitalCreate  # Явный импорт

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/hospitals/", response_model=Hospital)
def create_hospital(hospital: HospitalCreate, db: Session = Depends(get_db)):
    return hospital_service.create_hospital(db=db, hospital=hospital)

@app.get("/hospitals/", response_model=list[Hospital])
def read_hospitals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return hospital_service.get_hospitals(db=db, skip=skip, limit=limit)