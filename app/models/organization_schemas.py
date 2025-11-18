"""
Schemas Pydantic para Organizations
"""
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
import re

class OrganizationCreate(BaseModel):
    """Schema para crear una nueva organización"""
    name: str = Field(..., min_length=3, max_length=200, description="Nombre de la institución")
    contact_email: EmailStr = Field(..., description="Email de contacto principal")
    contact_phone: Optional[str] = Field(None, max_length=50)
    
    institution_type: str = Field(..., description="Tipo de institución")
    country: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    address: Optional[str] = None
    
    # Datos del admin inicial
    admin_name: str = Field(..., min_length=2, description="Nombre completo del administrador")
    admin_email: EmailStr = Field(..., description="Email del administrador")
    admin_password: str = Field(..., min_length=8, description="Contraseña del administrador")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()
    
    @validator('admin_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hospital General de México",
                "contact_email": "contacto@hospitalgral.mx",
                "contact_phone": "+52 55 1234 5678",
                "institution_type": "Hospital Público",
                "country": "México",
                "city": "Ciudad de México",
                "address": "Av. Reforma 123, Col. Centro",
                "admin_name": "Dr. Juan Pérez",
                "admin_email": "juan.perez@hospitalgral.mx",
                "admin_password": "SecurePass123"
            }
        }

class OrganizationResponse(BaseModel):
    """Schema para respuesta de organización"""
    id: int
    name: str
    slug: str
    contact_email: str
    institution_type: Optional[str]
    country: Optional[str]
    city: Optional[str]
    is_active: bool
    plan: str
    max_users: int
    created_at: datetime
    trial_ends_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class OrganizationStats(BaseModel):
    """Estadísticas de una organización"""
    id: int
    name: str
    slug: str
    total_users: int
    active_users: int
    total_checklists: int
    total_reminders: int
    plan: str
    is_active: bool
    created_at: datetime
    last_activity: Optional[datetime]
