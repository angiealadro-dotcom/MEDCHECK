from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    area: Optional[str] = None

class UserCreate(UserBase):
    password: str
    is_admin: bool = False  # Compatible con SQLAlchemy User model

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_admin: bool = False  # Compatible con SQLAlchemy User model
    is_active: bool = True
    
    # Propiedad de compatibilidad
    @property
    def role(self) -> str:
        return "admin" if self.is_admin else "enfermero"

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str
    role: str