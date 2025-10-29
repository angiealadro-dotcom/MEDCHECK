import snowflake.connector
from typing import Generator
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    """
    Crear una conexión a Snowflake usando las credenciales del .env
    """
    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'MEDCHECK_DB'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        )
        return conn
    except Exception as e:
        print(f"Error conectando a Snowflake: {e}")
        raise e

def get_snowflake_cursor() -> Generator:
    """
    Generador para manejar la conexión y cursor de Snowflake
    """
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    yield cursor
    
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def init_snowflake():
    """
    Inicializar la base de datos en Snowflake
    1. Crear warehouse si no existe
    2. Crear database
    3. Crear schema
    4. Crear tablas
    """
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        
        print("Creando database...")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('SNOWFLAKE_DATABASE', 'MEDCHECK_DB')}")
        print("Database creada o ya existe")
        
        print("Usando database...")
        cur.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE', 'MEDCHECK_DB')}")
        print("Database en uso")
        
        print("Creando schema...")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')}")
        print("Schema creado o ya existe")
        
        print("Usando schema...")
        cur.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')}")
        print("Schema en uso")
        
        print("Eliminando tabla users si existe...")
        cur.execute("DROP TABLE IF EXISTS users")
        print("Tabla users eliminada si existía")
        
        print("Creando tabla users...")
        cur.execute("""
        create table users (
            id integer autoincrement,
            username string not null unique,
            email string not null unique,
            password_hash string not null,
            full_name string,
            area string,
            role string not null default 'enfermero',
            active boolean default true,
            created_at timestamp_ntz default current_timestamp(),
            updated_at timestamp_ntz default current_timestamp(),
            primary key (id)
        )
        """)
        print("Tabla users creada")
        
        print("Verificando tabla users...")
        cur.execute("SHOW TABLES LIKE 'users'")
        tables = cur.fetchall()
        print(f"Tablas encontradas: {tables}")
        
        if len(tables) > 0:
            print("Describiendo tabla users...")
            cur.execute("DESC TABLE users")
            columns = cur.fetchall()
            for col in columns:
                print(f"Columna: {col}")
        
        # Crear tabla de configuración de alertas si no existe
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_configs (
            id INTEGER AUTOINCREMENT,
            area STRING,
            umbral_critico FLOAT DEFAULT 70.0,
            umbral_advertencia FLOAT DEFAULT 85.0,
            emails_adicionales ARRAY,
            notificar_supervisores BOOLEAN DEFAULT TRUE,
            intervalo_horas INTEGER DEFAULT 24,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
        """)
        

        
        # Crear tabla de historial de alertas
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER AUTOINCREMENT,
            config_id INTEGER,
            area STRING,
            tipo STRING,
            mensaje STRING,
            cumplimiento FLOAT,
            emails_notificados ARRAY,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id),
            FOREIGN KEY (config_id) REFERENCES alert_configs(id)
        )
        """)
        
        # Crear database si no existe
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('SNOWFLAKE_DATABASE', 'MEDCHECK_DB')}")
        
        # Usar la database
        cur.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE', 'MEDCHECK_DB')}")
        
        # Crear schema si no existe
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')}")
        
        # Crear tabla principal
        cur.execute("""
        CREATE TABLE IF NOT EXISTS checklist_entries (
            id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
            protocolo_etapa STRING NOT NULL,
            item STRING NOT NULL,
            cumple BOOLEAN NOT NULL,
            observaciones STRING,
            fecha_hora TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            usuario STRING NOT NULL,
            area STRING NOT NULL,
            turno STRING NOT NULL,
            metadatos VARIANT,
            PRIMARY KEY (id)
        )
        """)
        
        # Crear vista para análisis
        cur.execute("""
        CREATE OR REPLACE VIEW v_cumplimiento_diario AS
        SELECT 
            DATE(fecha_hora) as fecha,
            area,
            turno,
            COUNT(*) as total_registros,
            SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
            (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
        FROM checklist_entries
        GROUP BY fecha, area, turno
        ORDER BY fecha DESC
        """)
        
        print("Base de datos Snowflake inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"Error inicializando Snowflake: {e}")
        return False
        
    finally:
        cur.close()
        conn.close()

def migrate_from_sqlite():
    """
    Migrar datos desde SQLite a Snowflake
    """
    from app.db.database import SessionLocal, ChecklistEntry
    
    # Obtener datos de SQLite
    db = SessionLocal()
    entries = db.query(ChecklistEntry).all()
    
    if not entries:
        print("No hay datos para migrar desde SQLite")
        return
    
    # Conectar a Snowflake
    conn = get_snowflake_connection()
    cur = conn.cursor()
    
    try:
        # Insertar datos en Snowflake
        for entry in entries:
            cur.execute("""
            INSERT INTO checklist_entries (
                protocolo_etapa, item, cumple, observaciones,
                fecha_hora, usuario, area, turno, metadatos
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entry.protocolo_etapa,
                entry.item,
                entry.cumple,
                entry.observaciones,
                entry.fecha_hora,
                entry.usuario,
                entry.area,
                entry.turno,
                entry.metadatos
            ))
        
        conn.commit()
        print(f"Migrados {len(entries)} registros a Snowflake")
        
    except Exception as e:
        conn.rollback()
        print(f"Error migrando datos a Snowflake: {e}")
        
    finally:
        cur.close()
        conn.close()
        db.close()