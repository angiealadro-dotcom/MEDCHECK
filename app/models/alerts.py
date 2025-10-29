from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class AlertConfig(BaseModel):
    id: Optional[int] = None
    area: Optional[str] = None
    umbral_critico: float = Field(default=70.0, ge=0.0, le=100.0)
    umbral_advertencia: float = Field(default=85.0, ge=0.0, le=100.0)
    emails_adicionales: List[EmailStr] = []
    notificar_supervisores: bool = True
    intervalo_horas: int = Field(default=24, ge=1, le=72)
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "area": "UCI",
                "umbral_critico": 70.0,
                "umbral_advertencia": 85.0,
                "emails_adicionales": ["supervisor@hospital.com"],
                "notificar_supervisores": True,
                "intervalo_horas": 24,
                "activo": True
            }
        }