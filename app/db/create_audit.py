from app.db.snowflake_db import get_snowflake_connection

def create_audit_table():
    """
    Crear tabla de auditoría en Snowflake
    """
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        
        # Crear tabla de auditoría
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
            event_type STRING NOT NULL,
            username STRING NOT NULL,
            ip_address STRING NOT NULL,
            timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            details STRING,
            area STRING,
            role STRING,
            status STRING NOT NULL,
            user_agent STRING,
            session_id STRING,
            PRIMARY KEY (id)
        )
        """)
        
        # Crear vista para análisis de seguridad
        cur.execute("""
        CREATE OR REPLACE VIEW v_security_alerts AS
        SELECT 
            username,
            COUNT(CASE WHEN event_type = 'failed_login' THEN 1 END) as failed_logins,
            COUNT(CASE WHEN event_type = 'account_locked' THEN 1 END) as account_lockouts,
            COUNT(DISTINCT ip_address) as unique_ips,
            MIN(CASE WHEN status = 'failure' THEN timestamp END) as first_failure,
            MAX(CASE WHEN status = 'failure' THEN timestamp END) as last_failure
        FROM audit_logs
        WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
        GROUP BY username
        HAVING failed_logins > 3 OR account_lockouts > 0
        """)
        
        conn.commit()
        print("Tabla de auditoría creada exitosamente")
        return True
        
    except Exception as e:
        print(f"Error creando tabla de auditoría: {e}")
        return False
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_audit_table()