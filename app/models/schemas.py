from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ChecklistEntryBase(BaseModel):
    protocolo_etapa: str
    item: str
    cumple: bool
    observaciones: Optional[str] = None
    usuario: str
    area: str
    turno: str
    metadatos: Optional[Dict[str, Any]] = None

class ChecklistEntryCreate(ChecklistEntryBase):
    pass

class ChecklistEntry(ChecklistEntryBase):
    id: int
    fecha_hora: datetime

    class Config:
        from_attributes = True

class ChecklistForm(BaseModel):
    area: str
    turno: str
    items: Dict[str, Dict[str, bool]]
    observaciones: Optional[str] = None