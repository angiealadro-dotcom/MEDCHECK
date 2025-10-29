from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChecklistEntry(BaseModel):
    id: Optional[int] = None
    protocolo_etapa: str  # 'prescripcion', 'transcripcion', 'preparacion', 'administracion', 'registro'
    item: str
    cumple: bool
    observaciones: Optional[str] = None
    fecha_hora: datetime = datetime.now()
    usuario: str
    area: str
    turno: str  # 'mañana', 'tarde', 'noche'
    metadatos: Optional[dict] = None

class ChecklistSummary(BaseModel):
    total_registros: int
    cumplimiento_porcentaje: float
    items_criticos: list[str]
    areas_afectadas: list[str]