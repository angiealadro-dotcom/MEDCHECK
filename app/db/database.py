from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.user import Base
# Importar modelos para registrarlos en la metadata (no borrar)
from app.models.checklist_entry import ChecklistEntrySQL  # noqa: F401
from app.models.notification import WebPushSubscription  # noqa: F401
from app.models.reminder import Reminder  # noqa: F401
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configuración del engine según el tipo de base de datos
if settings.database_url.startswith("sqlite"):
    # SQLite: usar StaticPool para evitar problemas con threads
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug
    )

    # Habilitar foreign keys en SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
        cursor.close()
else:
    # PostgreSQL u otras bases de datos: usar pool de conexiones
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,  # Verificar conexiones antes de usar
        echo=settings.debug
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {e}")
        db.rollback()
        raise
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
        logger.info("✅ Tablas de base de datos verificadas/creadas")
    except OperationalError as e:
        msg = str(e).lower()
        if "already exists" in msg or "exists" in msg:
            # Otro worker ganó la carrera; continuar normalmente
            logger.info("[DB] Tablas ya existen (race condition resuelta). Continuando…")
        else:
            # Registrar y continuar para no bloquear el arranque
            logger.warning(f"[DB][warn] Error en create_all: {e}")
    except Exception as e:
        # Cualquier otro error no-critico tampoco debería tumbar la app en arranque
        logger.warning(f"[DB][warn] Excepción inesperada en create_all: {e}")

def check_db_connection():
    """Verifica que la conexión a la base de datos funcione"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✅ Conexión a base de datos verificada")
        return True
    except Exception as e:
        logger.error(f"❌ Error de conexión a base de datos: {e}")
        return False
