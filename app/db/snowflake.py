import os
from snowflake.connector import connect
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_snowflake_connection():
    """
    Crear conexión a Snowflake usando variables de entorno
    """
    try:
        conn = connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        return conn
    except Exception as e:
        print(f"Error conectando a Snowflake: {e}")
        raise e

def create_tables():
    """
    Crear tablas necesarias en Snowflake
    """
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        
        # Crear tabla principal de checklist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS checklist_entries (
            id NUMBER AUTOINCREMENT,
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
        
        # Crear vista para análisis de cumplimiento
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
        """)
        
    finally:
        conn.close()