"""
Migración a sistema multi-tenant
Agrega tabla organizations y actualiza estructura de base de datos
"""
import sqlite3
from datetime import datetime, timedelta

def migrate_to_multitenant():
    conn = sqlite3.connect('medcheck.db')
    cursor = conn.cursor()
    
    try:
        print("🔄 Iniciando migración a multi-tenancy...")
        
        # 1. Crear tabla organizations
        print("\n📦 Creando tabla organizations...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                contact_email VARCHAR(255) NOT NULL,
                contact_phone VARCHAR(50),
                institution_type VARCHAR(100),
                country VARCHAR(100),
                city VARCHAR(100),
                address TEXT,
                is_active BOOLEAN DEFAULT 1,
                plan VARCHAR(50) DEFAULT 'free',
                max_users INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trial_ends_at TIMESTAMP,
                logo_url VARCHAR(500),
                primary_color VARCHAR(7) DEFAULT '#0d6efd'
            )
        ''')
        print("✅ Tabla organizations creada")
        
        # 2. Crear organización DEMO (para el admin actual)
        print("\n🏥 Creando organización DEMO...")
        trial_end = datetime.now() + timedelta(days=365)  # 1 año de trial
        cursor.execute('''
            INSERT OR IGNORE INTO organizations 
            (id, name, slug, contact_email, institution_type, country, plan, max_users, trial_ends_at, is_active)
            VALUES (1, 'Organización Demo', 'demo', 'admin@medcheck.com', 'Hospital', 'México', 'enterprise', 999, ?, 1)
        ''', (trial_end.isoformat(),))
        print("✅ Organización DEMO creada (ID: 1)")
        
        # 3. Agregar columnas a users
        print("\n👥 Actualizando tabla users...")
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN organization_id INTEGER DEFAULT 1')
            print("   ✅ Columna organization_id agregada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ℹ️  Columna organization_id ya existe")
            else:
                raise
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0')
            print("   ✅ Columna is_super_admin agregada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ℹ️  Columna is_super_admin ya existe")
            else:
                raise
        
        # 4. Convertir admin actual en super_admin
        print("\n👑 Convirtiendo admin en super_admin...")
        cursor.execute('UPDATE users SET is_super_admin = 1, organization_id = 1 WHERE is_admin = 1')
        print(f"   ✅ {cursor.rowcount} usuario(s) actualizado(s)")
        
        # 5. Asignar organización DEMO a todos los usuarios existentes
        print("\n📋 Asignando organización DEMO a usuarios existentes...")
        cursor.execute('UPDATE users SET organization_id = 1 WHERE organization_id IS NULL')
        print(f"   ✅ {cursor.rowcount} usuario(s) asignado(s) a organización DEMO")
        
        # 6. Agregar organization_id a tablas de datos
        print("\n📊 Actualizando tablas de datos...")
        
        tables_to_update = [
            ('checklist_entries', 'id'),
            ('alerts', 'id'),
            ('reminders', 'id'),
            ('audit_log', 'id')
        ]
        
        for table, _ in tables_to_update:
            try:
                # Verificar si la tabla existe
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    print(f"   ⚠️  Tabla {table} no existe, omitiendo...")
                    continue
                
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN organization_id INTEGER DEFAULT 1')
                print(f"   ✅ Columna organization_id agregada a {table}")
                
                # Crear índice compuesto para mejorar rendimiento
                cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table}_org ON {table}(organization_id)')
                print(f"   ✅ Índice creado en {table}(organization_id)")
                
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ℹ️  Columna organization_id ya existe en {table}")
                else:
                    print(f"   ⚠️  Error en {table}: {e}")
        
        conn.commit()
        
        # 7. Verificar migración
        print("\n🔍 Verificando migración...")
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        print(f"   📊 Organizaciones: {org_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE organization_id IS NOT NULL")
        users_with_org = cursor.fetchone()[0]
        print(f"   👥 Usuarios con organización: {users_with_org}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_super_admin = 1")
        super_admins = cursor.fetchone()[0]
        print(f"   👑 Super admins: {super_admins}")
        
        print("\n✅ Migración completada exitosamente!")
        print("\n📋 Resumen:")
        print("   • Tabla organizations creada")
        print("   • Organización DEMO creada (ID: 1)")
        print("   • Usuario admin convertido a super_admin")
        print("   • Todos los datos existentes asignados a organización DEMO")
        print("   • Columnas organization_id agregadas a todas las tablas")
        print("   • Índices creados para optimizar consultas")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_to_multitenant()
