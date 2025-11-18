# 🚀 GUÍA RÁPIDA DE DEPLOYMENT - CLOUDFLARE PAGES

## 📋 VALORES NECESARIOS PARA CONFIGURACIÓN

### 🔑 VAPID Keys (para Push Notifications)

**VAPID_PUBLIC_KEY:**
```
BMTigRMOFtaEdVBXVfe89yrdMc2TE9kP7UZMV4-UlqQUb92eECqvGQAtnEvm7eSvg7if-JTkjh4LVIXnFe3ANgE
```

**VAPID_PRIVATE_KEY:**
```
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgkvXHOv1Sdb0Uv2N9
0R5/tzzTDz5iwdvxQ8jlQOIJqp+hRANCAATE4oETDhbWhHVQV1X3vPcq3THNkxPZ
D+1GTFePlJakFG/dnhAqrxkALZxL5u3kr4O4n/iU5I4eC1SF5xXtwDYB
-----END PRIVATE KEY-----
```

### 🔐 SECRET_KEY (generar nuevo para producción)

Ejecuta este comando en PowerShell para generar uno nuevo:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

O usa este que generé (CÁMBIALO después del deployment):
```
kOtfpn1InFw8PmkvOS8jVO84NKyiFrTG2zRGB3Qw-go
```

### 👤 CREDENCIALES INICIALES

**Super Admin:**
- Username: `admin`
- Password: `Admin123!`
- Email: `admin@medcheck.com`

⚠️ **IMPORTANTE:** Cambiar esta contraseña inmediatamente después del primer login

---

## 🎯 PASOS RÁPIDOS (15 minutos)

### 1. Crear Cuenta Cloudflare
- Ve a: https://dash.cloudflare.com/sign-up
- Crea cuenta gratuita
- Verifica email

### 2. Crear Base de Datos D1
1. Dashboard → **Workers & Pages** → **D1**
2. **Create database** → Nombre: `medcheck-db`
3. **COPIA EL DATABASE_ID** que aparece

### 3. Aplicar Schema SQL
1. En `medcheck-db` → **Console**
2. Copia TODO de: `migrations/001_initial_schema.sql`
3. Pega y **Execute**

### 4. Insertar Datos Iniciales
1. Mismo Console
2. Copia TODO de: `init_d1_data.sql`
3. Pega y **Execute**
4. Verifica: 1 organization, 1 user, 1 super admin

### 5. Conectar GitHub
1. **Workers & Pages** → **Pages** → **Create application**
2. **Connect to Git** → GitHub
3. Selecciona repo: `angiealadro-dotcom/MEDCHECK`
4. Branch: `dev/local-improvements-2025-11-17`
5. Framework: `None`
6. Build command: (vacío)
7. **Save and Deploy**

### 6. Configurar Variables de Entorno
**Settings** → **Environment variables** → Agregar:

**Production:**
- `ENVIRONMENT` = `production`
- `APP_NAME` = `MedCheck`
- `PYTHON_VERSION` = `3.11`
- `SECRET_KEY` = [el que generaste arriba] ✅ Encrypt
- `VAPID_PUBLIC_KEY` = [ver arriba] ✅ Encrypt
- `VAPID_PRIVATE_KEY` = [ver arriba - todo el bloque] ✅ Encrypt

### 7. Vincular D1
1. **Settings** → **Functions** → **D1 database bindings**
2. **Add binding**
3. Variable name: `DB`
4. Database: `medcheck-db`
5. **Save**

### 8. Desplegar
1. **Deployments** → **Create deployment**
2. Branch: `dev/local-improvements-2025-11-17`
3. **Save and Deploy**
4. Espera 2-5 minutos

### 9. ¡Listo! 🎉
- URL: `https://medcheck-xyz.pages.dev`
- Login con: admin / Admin123!
- Registra tu organización
- Cambia password de admin

---

## 🔍 TROUBLESHOOTING RÁPIDO

**Error de módulos:**
- Verifica que `requirements.txt` esté en la raíz

**Error de base de datos:**
- Verifica que D1 binding esté configurado como `DB`
- Verifica que ambos SQL scripts se hayan ejecutado

**No puedo hacer login:**
- Usuario: `admin`
- Password: `Admin123!` (con mayúsculas y signo de admiración)

**Errores de Python:**
- Verifica `PYTHON_VERSION` = `3.11`

---

## 📁 ARCHIVOS IMPORTANTES

- `migrations/001_initial_schema.sql` - Schema de base de datos
- `init_d1_data.sql` - Datos iniciales (admin + organización demo)
- `DEPLOY_MANUAL.md` - Guía completa paso a paso
- `.env.production.example` - Template de variables de entorno

---

## 🎓 DESPUÉS DEL DEPLOYMENT

1. **Cambiar password de admin** (Settings → Account)
2. **Crear tu organización** (Página principal → Registrar)
3. **Invitar usuarios** (una vez logueado)
4. **Configurar dominio custom** (opcional - Settings → Custom domains)

---

**¿Todo listo?** Sigue la guía completa en `DEPLOY_MANUAL.md` para más detalles.
