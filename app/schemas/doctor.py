from datetime import time, date
from pydantic import BaseModel

class DoctorBase(BaseModel):
    name: str
    hospital_id: int
    work_day: date
    shift_start: time
    shift_end: time

class DoctorCreate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True