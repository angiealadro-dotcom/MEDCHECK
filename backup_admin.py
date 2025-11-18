"""
Script para guardar credenciales del admin actual antes de migrar a multi-tenancy
"""
import json
from datetime import datetime
from app.db.database import SessionLocal
from app.models.user import User

def backup_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.is_admin == True).first()

        if admin:
            backup_data = {
                "backup_date": datetime.now().isoformat(),
                "admin_user": {
                    "id": admin.id,
                    "username": admin.username,
                    "email": admin.email,
                    "full_name": admin.full_name,
                    "hashed_password": admin.hashed_password,
                    "is_active": admin.is_active,
                    "is_admin": admin.is_admin
                },
                "note": "Admin original guardado antes de migración a multi-tenancy. Este usuario será convertido en SUPER_ADMIN."
            }

            # Guardar en archivo JSON
            with open('ADMIN_BACKUP.json', 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            print("✅ Admin guardado exitosamente!")
            print(f"📧 Email: {admin.email}")
            print(f"👤 Username: {admin.username}")
            print(f"📝 Full Name: {admin.full_name}")
            print(f"🔑 Password Hash: {admin.hashed_password[:50]}...")
            print("\n💾 Datos completos guardados en ADMIN_BACKUP.json")

            return backup_data
        else:
            print("❌ No se encontró usuario admin")
            return None

    finally:
        db.close()

if __name__ == "__main__":
    backup_admin()
