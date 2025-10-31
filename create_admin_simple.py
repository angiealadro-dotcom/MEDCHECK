"""
Script para crear usuario administrador en SQLite
"""
import os
from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("❌ El usuario 'admin' ya existe")
            print(f"   Email: {existing_admin.email}")
            print(f"   Admin: {existing_admin.is_admin}")
            return
        
        # Crear nuevo usuario admin
        hashed_password = pwd_context.hash("Admin123!")
        admin = User(
            username="admin",
            email="admin@medcheck.com",
            hashed_password=hashed_password,
            full_name="Administrador del Sistema",
            is_active=True,
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Usuario administrador creado exitosamente!")
        print("")
        print("📋 Credenciales:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: Admin123!")
        print(f"   Email: {admin.email}")
        print(f"   Es Admin: {admin.is_admin}")
        print("")
        print("🔗 Para iniciar sesión, ve a:")
        # Detectar puerto local (por defecto usamos 8001 que es el que usamos en desarrollo)
        port = os.getenv("APP_PORT") or os.getenv("PORT") or "8001"
        print(f"   http://localhost:{port}/login")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuario: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando usuario administrador...\n")
    create_admin()
