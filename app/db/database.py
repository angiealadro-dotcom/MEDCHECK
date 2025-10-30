from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base
# Importar modelos para registrarlos en la metadata (no borrar)
from app.models.checklist_entry import ChecklistEntrySQL  # noqa: F401
from app.config import settings

# Crear base engine SQLite
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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