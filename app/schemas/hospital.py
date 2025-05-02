from pydantic import BaseModel

class HospitalBase(BaseModel):
    name: str
    address: str

class HospitalCreate(HospitalBase):
    pass

class Hospital(HospitalBase):
    id: int

    class Config:
        from_attributes = True