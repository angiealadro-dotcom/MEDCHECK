# Guía de Despliegue en Cloudflare Pages + D1

## 📋 Requisitos Previos
1. Cuenta de Cloudflare (gratis)
2. Node.js y npm instalados
3. Git configurado

## 🚀 Pasos para Desplegar

### 1. Instalar Wrangler CLI
```bash
npm install -g wrangler
wrangler login
```

### 2. Crear Base de Datos D1
```bash
# Crear database
wrangler d1 create medcheck-db

# Copiar el database_id que se muestra y agregarlo a wrangler.toml
```

### 3. Aplicar Migraciones
```bash
# Crear archivo de migración SQL
# El contenido está en migrate_multitenant.py pero convertido a SQL puro
wrangler d1 execute medcheck-db --file=./migrations/001_initial_schema.sql
```

### 4. Configurar Secretos
```bash
# Secret key para JWT
wrangler secret put SECRET_KEY
# Ingresar: un string aleatorio seguro (ej: generado con openssl rand -hex 32)

# VAPID keys para push notifications
wrangler secret put VAPID_PRIVATE_KEY
wrangler secret put VAPID_PUBLIC_KEY
# Copiar de vapid_keys.json
```

### 5. Conectar Repositorio GitHub
1. Ir a Cloudflare Dashboard → Pages
2. Click "Create a project" → "Connect to Git"
3. Seleccionar repo: angiealadro-dotcom/MEDCHECK
4. Rama: dev/local-improvements-2025-11-17

### 6. Configurar Build
```
Build command: pip install -r requirements.txt
Build output directory: (vacío para FastAPI)
Framework preset: None
Python version: 3.11
```

### 7. Variables de Entorno en Cloudflare
En Settings → Environment Variables:
- `ENVIRONMENT=production`
- `APP_NAME=MedCheck`
- `DATABASE_URL` se configura automáticamente con D1

### 8. Custom Domain (Opcional)
Settings → Custom domains → Add custom domain
Ejemplo: medcheck.tudominio.com

## 📊 Estructura de Base de Datos

Cloudflare D1 es SQLite serverless, compatible 100% con tu código actual.

**Ventajas:**
- Gratis hasta 100,000 lecturas/día
- 5GB de almacenamiento
- Backups automáticos
- Geo-replicación

**Límites del Plan Gratuito:**
- 100K lecturas/día
- 50K escrituras/día
- 10 databases
- Perfecto para 50-100 organizaciones pequeñas

## 🔐 Seguridad

Cada organización tiene sus datos aislados con `organization_id`.
Los queries filtran automáticamente por organización.
El super admin puede ver todo.

## 🎯 Acceso al Panel de Super Admin

URL: `https://tudominio.pages.dev/organizations/list`

Credenciales (guardadas en ADMIN_BACKUP.json):
- Usuario: admin
- Email: admin@medcheck.com

## 📈 Monitoreo

Cloudflare Dashboard muestra:
- Requests por día
- Tiempo de respuesta
- Errores
- Uso de D1

## 🔄 Actualizar Código

```bash
git add .
git commit -m "feat: update"
git push origin dev/local-improvements-2025-11-17
```

Cloudflare Pages redespliega automáticamente.

## 💰 Costos

**Plan Gratuito:**
- Cloudflare Pages: Gratis ilimitado
- D1: Gratis hasta 100K lecturas/día
- Workers: 100K requests/día gratis

**Para escalar:**
- D1 Paid: $5/mes → 1 millón lecturas/día
- Workers Paid: $5/mes → 10 millones requests/mes

## 📞 Soporte

Si necesitas ayuda:
1. Cloudflare Discord: https://discord.gg/cloudflaredev
2. Docs: https://developers.cloudflare.com/pages/
3. D1 Docs: https://developers.cloudflare.com/d1/
