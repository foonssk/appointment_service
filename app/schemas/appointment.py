from datetime import datetime
from pydantic import BaseModel

class AppointmentBase(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: datetime

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

    class Config:
        from_attributes = True