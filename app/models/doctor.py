from sqlalchemy import Column, Integer, String, Time, ForeignKey, Date
from .base import Base

class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hospital_id = Column(Integer, ForeignKey('hospitals.id'), nullable=False)
    work_day = Column(Date, nullable=False)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)