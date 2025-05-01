from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Appointment(BaseModel):
    id: int
    pet_name: str
    owner_name: str
    appointment_time: datetime
    reason: Optional[str] = None
