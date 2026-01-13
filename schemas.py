from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class JobCreate(BaseModel):
    company: str
    role: str
    status: str
