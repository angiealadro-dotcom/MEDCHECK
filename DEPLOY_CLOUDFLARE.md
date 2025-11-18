# Cloudflare Pages Deployment - MedCheck

## 🚀 Pasos para Desplegar

### 1️⃣ Crear cuenta en Cloudflare (si no tienes)
Ve a: https://dash.cloudflare.com/sign-up

### 2️⃣ Instalar Wrangler CLI
Abre PowerShell y ejecuta:
```powershell
npm install -g wrangler
wrangler login
```

Esto abrirá tu navegador para autorizar Wrangler.

### 3️⃣ Crear base de datos D1
```powershell
wrangler d1 create medcheck-db
```

Copia el `database_id` que aparece y pégalo en `wrangler.toml` (línea 7).

### 4️⃣ Aplicar migraciones a D1
```powershell
wrangler d1 execute medcheck-db --file=./migrations/001_initial_schema.sql
```

### 5️⃣ Configurar secretos
```powershell
# Secret key para JWT (genera uno aleatorio)
wrangler secret put SECRET_KEY
# Pega este valor: medcheck-secret-key-2025-production-change-this

# VAPID keys para notificaciones
wrangler secret put VAPID_PRIVATE_KEY
# Copia el valor de vapid_keys.json -> private_key

wrangler secret put VAPID_PUBLIC_KEY
# Copia el valor de vapid_keys.json -> public_key
```

### 6️⃣ Conectar GitHub a Cloudflare Pages

**Opción A: Desde Cloudflare Dashboard (MÁS FÁCIL)**
1. Ve a: https://dash.cloudflare.com/
2. Haz clic en "Workers & Pages" en el menú izquierdo
3. Click en "Create application"
4. Tab "Pages" → "Connect to Git"
5. Autoriza GitHub
6. Selecciona el repositorio: `angiealadro-dotcom/MEDCHECK`
7. Branch: `dev/local-improvements-2025-11-17`
8. Framework preset: **None** (o Python)
9. Build command: `pip install -r requirements.txt`
10. Build output directory: **(dejar vacío)**
11. Root directory: **(dejar vacío)**

**Variables de Entorno a agregar:**
En "Environment variables":
- `PYTHON_VERSION` = `3.11`
- `ENVIRONMENT` = `production`
- `APP_NAME` = `MedCheck`

12. Click "Save and Deploy"

### 7️⃣ Configurar D1 Binding en Pages
1. Una vez creado el proyecto en Pages
2. Ve a Settings → Functions
3. En "D1 database bindings" → Add binding
   - Variable name: `DB`
   - D1 database: Selecciona `medcheck-db`
4. Save

### 8️⃣ Verificar deployment
Tu app estará en: `https://medcheck-[random].pages.dev`

---

## 🔧 Troubleshooting

### Error: "Python version not found"
Agregar `runtime.txt` con:
```
python-3.11
```

### Error: "Module not found"
Verificar que `requirements.txt` tenga todas las dependencias.

### Error: "Database not configured"
Verificar que el D1 binding esté configurado correctamente en Settings → Functions.

### Error: "Secret key not found"
Configurar los secretos con `wrangler secret put SECRET_KEY`.

---

## 📊 Monitoreo

Una vez desplegado, puedes ver:
- Requests por día
- Errores
- Tiempo de respuesta
- Uso de D1

En: Dashboard → Workers & Pages → Tu proyecto → Analytics

---

## 🔄 Actualizar la aplicación

Solo haz push a GitHub:
```powershell
git add .
git commit -m "Update: descripción del cambio"
git push origin dev/local-improvements-2025-11-17
```

Cloudflare Pages redesplegará automáticamente.

---

## 💰 Costos

**GRATIS incluye:**
- Requests ilimitados
- 100K lecturas D1/día
- 50K escrituras D1/día
- Ancho de banda ilimitado
- SSL gratis
- CDN global

**Límites del plan gratuito:**
- 100K lecturas/día en D1
- 500 builds/mes
- 100 proyectos activos

Para 50-100 organizaciones pequeñas, el plan gratuito es suficiente.

---

## 🌐 Custom Domain (Opcional)

1. Ve a Workers & Pages → Tu proyecto → Custom domains
2. Click "Set up a custom domain"
3. Ingresa tu dominio (ej: medcheck.tudominio.com)
4. Sigue las instrucciones para configurar DNS

---

## ✅ Checklist de Deploy

- [ ] Cuenta de Cloudflare creada
- [ ] Wrangler CLI instalado y autenticado
- [ ] Base de datos D1 creada
- [ ] Migraciones aplicadas
- [ ] Secretos configurados (SECRET_KEY, VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY)
- [ ] Repositorio conectado a Cloudflare Pages
- [ ] D1 binding configurado
- [ ] Primer deploy exitoso
- [ ] App funcionando en `*.pages.dev`

---

## 🔐 Acceso inicial

**Super Admin:**
- Usuario: `admin`
- Password: (el que tenías configurado)
- URL: `https://tu-app.pages.dev/organizations/list`

**Nueva Organización creada:**
- Usuario: `angiealadro`
- Password: (el que pusiste en el registro)
- URL: `https://tu-app.pages.dev/login`

---

¡Tu aplicación multi-tenant estará disponible globalmente! 🌍
