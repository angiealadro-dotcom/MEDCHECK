from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Crear base engine SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./medcheck.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    checklist_entries = relationship("ChecklistEntry", back_populates="user")

class ChecklistEntry(Base):
    __tablename__ = "checklist_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    protocolo_etapa = Column(String, index=True)  # prescripcion, transcripcion, preparacion, administracion, registro
    item = Column(String)
    cumple = Column(Boolean)
    observaciones = Column(String, nullable=True)
    fecha_hora = Column(DateTime, default=datetime.now)
    area = Column(String, index=True)
    turno = Column(String)  # mañana, tarde, noche
    metadatos = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="checklist_entries")

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas
def create_tables():
    Base.metadata.create_all(bind=engine)