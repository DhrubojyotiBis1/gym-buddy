from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from database import Base
from models.enums import UserRole

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    role = Column(Enum(UserRole, name="userrole", create_type=True), index=True) #TODO: put enum in registrary
    age = Column(Integer)
    gym_yoe = Column(Integer)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    modified_at = Column(DateTime(timezone=True),onupdate=func.now())
