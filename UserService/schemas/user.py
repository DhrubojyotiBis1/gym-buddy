from pydantic import BaseModel
from typing import Optional
from models.enums import UserRole

class UserCreate(BaseModel):
    name: str
    email: str
    hashed_password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gym_yoe: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    phone: str
    age: int
    gym_yoe: int

    class Config:
        orm_mode = True