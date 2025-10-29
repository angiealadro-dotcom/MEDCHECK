from app.db.snowflake import get_snowflake_connection
from passlib.hash import bcrypt

def create_admin_user():
    """
    Crear usuario administrador si no existe
    """
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        
        # Verificar si el usuario admin ya existe
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@medcheck.com'")
        if cursor.fetchone()[0] == 0:
            # Crear hash de la contraseña
            hashed_password = bcrypt.hash("admin123")
            
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
            print("Usuario administrador creado exitosamente!")
            print("Email: admin@medcheck.com")
            print("Contraseña: admin123")
        else:
            print("El usuario administrador ya existe")
            
    except Exception as e:
        print(f"Error creando usuario administrador: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()