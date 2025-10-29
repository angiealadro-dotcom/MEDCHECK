from app.db.snowflake_db import get_snowflake_connection

def create_users_table():
    """
    Crear tabla de usuarios en Snowflake
    """
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        
        # Crear tabla de usuarios
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
            username STRING NOT NULL UNIQUE,
            email STRING NOT NULL UNIQUE,
            hashed_password STRING NOT NULL,
            full_name STRING,
            role STRING NOT NULL DEFAULT 'enfermero',
            area STRING,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
        """)
        
        # Crear vista para auditoría de usuarios
        cur.execute("""
        CREATE OR REPLACE VIEW v_user_activity AS
        SELECT 
            u.username,
            u.role,
            u.area,
            COUNT(c.id) as total_checklists,
            AVG(CASE WHEN c.cumple THEN 1 ELSE 0 END) * 100 as porcentaje_cumplimiento
        FROM users u
        LEFT JOIN checklist_entries c ON u.username = c.usuario
        GROUP BY u.username, u.role, u.area
        """)
        
        # Insertar usuario admin por defecto
        cur.execute("""
        INSERT INTO users (username, email, hashed_password, full_name, role)
        SELECT 'admin', 'admin@medcheck.com', 
               '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNZpc8fpn82Uu', 
               'Administrator', 'admin'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin')
        """)
        
        conn.commit()
        print("Tabla de usuarios creada exitosamente")
        return True
        
    except Exception as e:
        print(f"Error creando tabla de usuarios: {e}")
        return False
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_users_table()