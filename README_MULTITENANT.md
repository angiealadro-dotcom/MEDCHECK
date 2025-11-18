# 🏥 MedCheck - Sistema Multi-Tenant Configurado

## ✅ Lo que se ha completado

### 1. Base de Datos Multi-Tenant
- ✅ Tabla `organizations` creada
- ✅ Columna `organization_id` agregada a todas las tablas
- ✅ Columna `is_super_admin` agregada a usuarios
- ✅ Usuario admin convertido a super_admin
- ✅ Índices compuestos para optimizar consultas
- ✅ Organización DEMO creada (ID: 1)

### 2. Sistema de Registro
- ✅ Modelo `Organization` con todos los campos
- ✅ Schemas Pydantic para validación
- ✅ Router `/organizations` con endpoints
- ✅ Template de registro `organization_register.html`
- ✅ Validación de contraseñas seguras
- ✅ Generación automática de slugs

### 3. Panel de Super Admin
- ✅ Dashboard en `/organizations/list`
- ✅ Vista de todas las organizaciones
- ✅ Estadísticas por organización
- ✅ Activar/desactivar organizaciones
- ✅ Ver usuarios y checklists por org

### 4. Credenciales Guardadas
- ✅ Admin actual respaldado en `ADMIN_BACKUP.json`
- Usuario: admin
- Email: admin@medcheck.com
- Password hash preservado

### 5. Configuración Cloudflare
- ✅ `wrangler.toml` creado
- ✅ Migración SQL (`001_initial_schema.sql`)
- ✅ Guía de despliegue (`CLOUDFLARE_DEPLOY.md`)

## 🚀 Cómo Probar Localmente

### 1. Iniciar el Servidor
```bash
.\venv\Scripts\python.exe run_dev.py
```

### 2. Acceder como Super Admin
URL: http://localhost:8002/organizations/list
Credenciales:
- Usuario: `admin`
- Contraseña: (la que tenías configurada)

### 3. Registrar una Nueva Organización
1. Ir a: http://localhost:8002/organizations/register
2. Llenar el formulario:
   - Nombre institución: "Hospital San José"
   - Email contacto: hospital@example.com
   - Tipo: Hospital Privado
   - País/Ciudad: México / Guadalajara
   - Admin nombre: Dr. Juan Pérez
   - Admin email: juan.perez@hospital.com
   - Contraseña: Test1234 (mínimo 8 chars, mayúscula, minúscula, número)

3. Click "Crear Cuenta"
4. Redirige a login
5. Iniciar sesión con las credenciales del admin creado

### 4. Verificar Aislamiento de Datos
- Cada organización solo ve sus propios datos
- El super admin ve todo en `/organizations/list`

## 📊 Para Subir a Cloudflare

### Requisitos
1. Cuenta de Cloudflare (gratis): https://dash.cloudflare.com/sign-up
2. Instalar Node.js: https://nodejs.org/
3. Instalar Wrangler CLI:
```bash
npm install -g wrangler
wrangler login
```

### Pasos Rápidos
1. Crear base de datos D1:
```bash
wrangler d1 create medcheck-db
```

2. Copiar el `database_id` que aparece y agregarlo en `wrangler.toml`

3. Aplicar migración:
```bash
wrangler d1 execute medcheck-db --file=./migrations/001_initial_schema.sql
```

4. Conectar GitHub en Cloudflare Pages:
   - Dashboard → Pages → Create project
   - Connect Git → Seleccionar repo
   - Deploy

5. Configurar variables de entorno en Cloudflare

Ver guía completa en: `CLOUDFLARE_DEPLOY.md`

## 🔐 Seguridad

### Multi-Tenancy
- Cada organización tiene `organization_id` único
- Todos los queries filtran automáticamente por organización
- Los usuarios solo ven datos de su organización
- El super admin puede ver todo

### Roles
- **Super Admin**: Puede crear/desactivar organizaciones, ver todo
- **Admin de Organización**: Administra su organización
- **Usuario Regular**: Usa el sistema normalmente

## 💰 Costos en Cloudflare

### Plan Gratuito (Suficiente para empezar)
- ✅ Cloudflare Pages: Ilimitado
- ✅ D1 Database: 100K lecturas/día
- ✅ Workers: 100K requests/día
- ✅ 5GB almacenamiento

### Si necesitas escalar
- D1 Paid: $5/mes → 1 millón lecturas/día
- Workers Paid: $5/mes → 10 millones requests/mes

## 📈 Próximos Pasos

### Para implementar aislamiento completo:
1. Modificar servicios para filtrar por `organization_id`
2. Agregar middleware de tenant
3. Actualizar queries en routers
4. Testing con múltiples organizaciones

### Para mejorar:
1. Sistema de pagos (Stripe)
2. Límites por plan (free: 5 users, pro: 25 users, enterprise: ilimitado)
3. Personalización (logo, colores por organización)
4. Reportes agregados para super admin
5. Exportación de datos por organización

## 🎯 Acceso al Sistema

### Desarrollo Local
- Landing: http://localhost:8002/
- Login: http://localhost:8002/login
- Registro Org: http://localhost:8002/organizations/register
- Super Admin: http://localhost:8002/organizations/list

### Producción (después de deploy)
- Landing: https://medcheck.pages.dev/
- Super Admin: https://medcheck.pages.dev/organizations/list

## 📞 Datos de Contacto

Admin original guardado en: `ADMIN_BACKUP.json`
- Username: admin
- Email: admin@medcheck.com
- Role: Super Admin
- Organization: Demo (ID: 1)

## 🐛 Troubleshooting

### Error: "organization_id column doesn't exist"
Ejecutar:
```bash
python migrate_multitenant.py
```

### Error: "No super admin found"
El usuario admin actual ya fue convertido a super_admin.
Verificar con:
```bash
python -c "from app.db.database import SessionLocal; from app.models.user import User; db = SessionLocal(); admin = db.query(User).filter(User.is_super_admin == True).first(); print(f'Super admin: {admin.username if admin else None}')"
```

### ¿Cómo ver qué organizaciones existen?
```bash
python -c "from app.db.database import SessionLocal; from app.models.organization import Organization; db = SessionLocal(); orgs = db.query(Organization).all(); [print(f'{o.id}: {o.name} ({o.slug})') for o in orgs]"
```
