from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from datetime import datetime
from app.models.user import Base


class ChecklistEntrySQL(Base):
    __tablename__ = "checklist_entries"

    id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    area = Column(String, index=True, nullable=False)
    turno = Column(String, index=True, nullable=False)  # manana/tarde/noche
    protocolo_etapa = Column(String, index=True, nullable=False)  # prescripcion/preparacion/administracion
    item = Column(String, index=True, nullable=False)
    cumple = Column(Boolean, default=False, nullable=False)
    observaciones = Column(String, nullable=True)
    usuario = Column(String, index=True, nullable=True)
    metadatos = Column(JSON, nullable=True)
