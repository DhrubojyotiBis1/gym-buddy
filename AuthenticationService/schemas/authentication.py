from pydantic import BaseModel
from typing import Optional

class Auth(BaseModel):
    access: Optional[str] = None
    refres: Optional[str] = None

class SignupUser(BaseModel):
    name: str
    email: str
    hashed_password: str

class SigninUser(BaseModel):
    email: str
    hashed_password: str