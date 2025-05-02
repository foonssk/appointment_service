from sqlalchemy import Column, Integer, String
from .base import Base

class Hospital(Base):
    __tablename__ = 'hospitals'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)