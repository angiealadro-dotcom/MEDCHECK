"""
Modelo de Organization para multi-tenancy
Cada organización tendrá sus propios datos aislados
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # Para subdominios/URLs
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    
    # Info de la institución
    institution_type = Column(String(100))  # Hospital, Clínica, Centro de Salud
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    
    # Estado y plan
    is_active = Column(Boolean, default=True)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    max_users = Column(Integer, default=5)  # Límite según plan
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trial_ends_at = Column(DateTime, nullable=True)  # Para trial de 30 días
    
    # Configuración personalizada
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#0d6efd")  # Color de marca
    
    # Relación con usuarios
    # users = relationship("User", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"
