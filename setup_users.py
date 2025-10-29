from app.db.snowflake import get_snowflake_connection
import hashlib
import os

def setup_users_table():
    """
    Crear tabla de usuarios y usuario administrador
    """
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        
        # Crear tabla de usuarios si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id NUMBER AUTOINCREMENT START 1 INCREMENT 1,
            email STRING NOT NULL UNIQUE,
            password_hash STRING NOT NULL,
            nombre STRING NOT NULL,
            apellido STRING NOT NULL,
            role STRING NOT NULL,
            area STRING,
            activo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
        """)
        
        # Verificar si el usuario admin ya existe
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@medcheck.com'")
        if cursor.fetchone()[0] == 0:
            # Crear salt y hash de la contraseña
            salt = os.urandom(32)
            password = "admin123".encode('utf-8')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
            hashed_password = salt.hex() + ':' + hash_obj.hex()
            
            # Insertar usuario admin
            cursor.execute("""
                INSERT INTO users (
                    email,
                    password_hash,
                    nombre,
                    apellido,
                    role,
                    area,
                    activo
                ) VALUES (
                    'admin@medcheck.com',
                    %s,
                    'Administrador',
                    'Sistema',
                    'admin',
                    NULL,
                    TRUE
                )
            """, (hashed_password,))
            
            conn.commit()
            print("¡Usuario administrador creado exitosamente!")
            print("Email: admin@medcheck.com")
            print("Contraseña: admin123")
        else:
            print("El usuario administrador ya existe")
            
    except Exception as e:
        print(f"Error en la configuración: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    setup_users_table()