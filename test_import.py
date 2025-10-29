import sys
print("Python version:", sys.version)
print("Importando módulos...")

try:
    from app.config import settings
    print("✅ Config cargado")
    print(f"   App: {settings.app_name}")
    print(f"   DB: {settings.database_url}")
except Exception as e:
    print(f"❌ Error en config: {e}")
    sys.exit(1)

try:
    from app.models.user import User, Base
    print("✅ Modelos cargados")
except Exception as e:
    print(f"❌ Error en modelos: {e}")
    sys.exit(1)

try:
    from app.db.database import engine, create_tables
    print("✅ Database engine creado")
    create_tables()
    print("✅ Tablas creadas")
except Exception as e:
    print(f"❌ Error en database: {e}")
    sys.exit(1)

try:
    from app.auth.users import get_password_hash
    print("✅ Auth cargado")
except Exception as e:
    print(f"❌ Error en auth: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✅ App principal cargada")
    print("\n🎉 ¡Todo cargado correctamente!")
    print("\nIniciando servidor...")
except Exception as e:
    print(f"❌ Error en main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
