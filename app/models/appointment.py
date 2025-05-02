from sqlalchemy import Column, Integer, ForeignKey, DateTime
from .base import Base

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    patient_id = Column(Integer, nullable=False)
    appointment_date = Column(DateTime, nullable=False)