from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")   # user | admin

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    company = Column(String)
    role = Column(String)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned admin