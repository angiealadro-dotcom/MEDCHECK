from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
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
    """
    Crea las tablas si no existen.
    En despliegues con múltiples workers puede ocurrir una condición de carrera
    durante create_all(); si otro worker ya creó la tabla, ignoramos el error
    "table already exists" para no tumbar el servicio.
    """
    try:
        # checkfirst=True es el valor por defecto, pero dejamos claro el intento
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except OperationalError as e:
        msg = str(e).lower()
        if "already exists" in msg or "exists" in msg:
            # Otro worker ganó la carrera; continuar normalmente
            print("[DB] Tablas ya existen (race condition resuelta). Continuando…")
        else:
            # Registrar y continuar para no bloquear el arranque
            print(f"[DB][warn] Error en create_all: {e}")
    except Exception as e:
        # Cualquier otro error no-critico tampoco debería tumbar la app en arranque
        print(f"[DB][warn] Excepción inesperada en create_all: {e}")