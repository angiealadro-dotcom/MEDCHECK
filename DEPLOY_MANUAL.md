# Guía de Deployment Manual a Cloudflare Pages

Esta guía te permite desplegar MedCheck a Cloudflare Pages sin necesidad de instalar Node.js o Wrangler CLI, usando solo el dashboard web de Cloudflare.

## 📋 Pre-requisitos

1. Cuenta de GitHub con el repositorio MedCheck
2. Cuenta de Cloudflare (gratis en https://dash.cloudflare.com/sign-up)

## 🚀 Pasos de Deployment

### Paso 1: Crear Cuenta en Cloudflare

1. Ve a https://dash.cloudflare.com/sign-up
2. Crea una cuenta gratuita
3. Verifica tu email
4. Inicia sesión en el dashboard

### Paso 2: Obtener tu Account ID

1. En el dashboard de Cloudflare, ve a cualquier sección
2. En la barra lateral derecha, busca **Account ID**
3. Cópialo (lo necesitarás más adelante)

### Paso 3: Crear Base de Datos D1

1. En el dashboard, ve a **Workers & Pages** (menú izquierdo)
2. Selecciona la pestaña **D1**
3. Click en **Create database**
4. Nombre: `medcheck-db`
5. Click **Create**
6. **IMPORTANTE**: Copia el **Database ID** que aparece

### Paso 4: Aplicar Schema SQL a D1

1. En la página de tu base de datos `medcheck-db`
2. Ve a la pestaña **Console**
3. Copia TODO el contenido del archivo `migrations/001_initial_schema.sql`
4. Pégalo en el console
5. Click en **Execute**
6. Verifica que no haya errores (debe mostrar "Success")

### Paso 5: Inicializar Datos en D1

1. En el mismo Console de D1
2. Copia TODO el contenido del archivo `init_d1_data.sql`
3. Pégalo en el console
4. Click en **Execute**
5. Verifica que muestre:
   - Organizations created: 1
   - Users created: 1
   - Super admins: 1

### Paso 6: Conectar GitHub a Cloudflare Pages

1. En el dashboard de Cloudflare, ve a **Workers & Pages**
2. Selecciona la pestaña **Pages**
3. Click en **Create application**
4. Click en **Connect to Git**
5. Selecciona **GitHub**
6. Autoriza Cloudflare a acceder a tu cuenta de GitHub
7. Selecciona el repositorio: `angiealadro-dotcom/MEDCHECK`
8. Click **Begin setup**

### Paso 7: Configurar Build Settings

En la configuración del proyecto:

**Project name:** `medcheck` (o el que prefieras)

**Production branch:** `dev/local-improvements-2025-11-17`

**Framework preset:** `None`

**Build command:** (dejar vacío)

**Build output directory:** `/`

**Root directory:** `/`

Click en **Save and Deploy** (por ahora, fallará pero está bien)

### Paso 8: Configurar Variables de Entorno

1. Ve a tu proyecto en Pages
2. Click en **Settings** → **Environment variables**
3. Agrega las siguientes variables:

#### Variables Públicas (Production):

| Variable Name | Value |
|--------------|-------|
| `ENVIRONMENT` | `production` |
| `APP_NAME` | `MedCheck` |
| `PYTHON_VERSION` | `3.11` |

#### Secrets (Encrypted):

1. Genera un SECRET_KEY:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copia el resultado y agrégalo como **SECRET_KEY**

2. Lee las VAPID keys de tu archivo `vapid_keys.json`:
   - Abre el archivo
   - Copia el valor de `public_key` → Agrégalo como **VAPID_PUBLIC_KEY**
   - Copia el valor de `private_key` → Agrégalo como **VAPID_PRIVATE_KEY**

Para agregar secrets:
- Click en **Add variable**
- Marca **Encrypt** para SECRET_KEY y VAPID keys
- **Service:** Production
- Guarda cada una

### Paso 9: Configurar D1 Binding

1. En Settings de tu proyecto Pages
2. Ve a **Functions** → **D1 database bindings**
3. Click en **Add binding**
4. **Variable name:** `DB` (exactamente así, en mayúsculas)
5. **D1 database:** Selecciona `medcheck-db`
6. Click **Save**

Esto vinculará automáticamente la base de datos D1 a tu aplicación.

### Paso 10: Actualizar wrangler.toml (opcional)

Si quieres tener el archivo actualizado en tu repo:

1. Edita `wrangler.toml`
2. Reemplaza `YOUR_ACCOUNT_ID` con tu Account ID del Paso 2
3. Reemplaza `YOUR_DATABASE_ID` con el Database ID del Paso 3
4. Commit y push los cambios

### Paso 11: Desplegar

1. Ve a **Deployments** en tu proyecto Pages
2. Click en **Create deployment**
3. Selecciona la rama: `dev/local-improvements-2025-11-17`
4. Click **Save and Deploy**
5. Espera 2-5 minutos mientras se construye

### Paso 12: Verificar Deployment

Una vez completado el deployment:

1. Verás una URL como: `https://medcheck-xyz.pages.dev`
2. Haz click en **Visit site**
3. Deberías ver la página de login de MedCheck

#### Probar el Sistema:

1. **Registrar una organización:**
   - Ve a la página principal
   - Click en "Registrar Organización"
   - Llena el formulario
   - Crea tu cuenta

2. **Login con Super Admin:**
   - Usuario: `admin`
   - Password: `Admin123!`
   - **IMPORTANTE:** Cambia la contraseña después del primer login

3. **Ver Dashboard de Super Admin:**
   - Una vez logueado como admin
   - Ve a `/organizations/list`
   - Deberías ver todas las organizaciones registradas

## 🔧 Troubleshooting

### Error: "Module not found"
- Verifica que `requirements.txt` esté en la raíz del repositorio
- Verifica que todas las dependencias estén listadas

### Error: "Database connection failed"
- Verifica que el D1 binding esté configurado correctamente (nombre: `DB`)
- Verifica que la base de datos esté creada y tenga el schema aplicado

### Error: "Invalid credentials"
- Usuario super admin: `admin`
- Password: `Admin123!` (cambiar después del primer login)
- Verifica que el script `init_d1_data.sql` se haya ejecutado correctamente

### La aplicación no inicia
- Ve a **Functions** → **Logs** en tu proyecto Pages
- Busca errores en el deployment log
- Verifica todas las variables de entorno

### Errores de Python
- Asegúrate que `PYTHON_VERSION` esté en `3.11`
- Cloudflare Pages soporta Python 3.7, 3.8, y 3.11

## 📊 Monitoreo

### Ver Logs:
1. Ve a tu proyecto en Pages
2. **Functions** → **Logs**
3. Filtra por errores o busca requests específicos

### Analytics:
1. **Analytics** → **Web Analytics**
2. Ve requests, pages views, etc.

### D1 Usage:
1. Ve a tu base de datos en **D1**
2. Verás:
   - Total queries
   - Read/Write operations
   - Storage used

## 💰 Costos

### Plan Gratuito incluye:
- **Cloudflare Pages:** Unlimited requests, unlimited bandwidth
- **Cloudflare D1:** 
  - 5 GB storage
  - 5 million reads/day
  - 100,000 writes/day
- **Workers:** 100,000 requests/day

Para un hospital pequeño/mediano, el plan gratuito es más que suficiente.

## 🔄 Actualizaciones

Cada vez que hagas `git push` a la rama `dev/local-improvements-2025-11-17`:
1. Cloudflare detectará los cambios automáticamente
2. Iniciará un nuevo deployment
3. Tomará 2-5 minutos
4. La nueva versión estará live

Para ver el progreso:
- Ve a **Deployments** en tu proyecto Pages
- Verás el status del deployment

## 🌐 Custom Domain (Opcional)

Si tienes un dominio:

1. Ve a **Custom domains** en tu proyecto Pages
2. Click **Set up a custom domain**
3. Ingresa tu dominio (ej: `medcheck.tudominio.com`)
4. Sigue las instrucciones para configurar DNS
5. Cloudflare te dará un CNAME record para agregar a tu DNS

## 🔐 Seguridad Post-Deployment

1. **Cambiar password de admin:**
   - Login como admin
   - Ve a configuración de usuario
   - Cambia la contraseña de `Admin123!` a una segura

2. **Configurar CORS (si usas custom domain):**
   - Agrega variable de entorno `ALLOWED_ORIGINS`
   - Valor: `https://tudominio.com,https://www.tudominio.com`

3. **Monitorear logs regularmente:**
   - Revisa intentos de login fallidos
   - Verifica actividad inusual

## ✅ Checklist de Deployment

- [ ] Cuenta de Cloudflare creada
- [ ] Account ID obtenido
- [ ] Base de datos D1 `medcheck-db` creada
- [ ] Database ID copiado
- [ ] Schema SQL aplicado (001_initial_schema.sql)
- [ ] Datos iniciales insertados (init_d1_data.sql)
- [ ] Verificado: 1 organización, 1 usuario, 1 super admin
- [ ] GitHub conectado a Cloudflare Pages
- [ ] Proyecto Pages creado (nombre: medcheck)
- [ ] Variables de entorno configuradas (ENVIRONMENT, APP_NAME, PYTHON_VERSION)
- [ ] Secrets configurados (SECRET_KEY, VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY)
- [ ] D1 binding configurado (DB → medcheck-db)
- [ ] Deployment ejecutado exitosamente
- [ ] Sitio accesible en *.pages.dev
- [ ] Registro de organización funciona
- [ ] Login funciona
- [ ] Super admin puede acceder a /organizations/list
- [ ] Password de admin cambiado

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs en Functions → Logs
2. Verifica todas las configuraciones en este checklist
3. Consulta la documentación de Cloudflare Pages: https://developers.cloudflare.com/pages/
4. Consulta la documentación de D1: https://developers.cloudflare.com/d1/

---

**¡Tu aplicación MedCheck multi-tenant está lista para producción en Cloudflare! 🎉**

Las organizaciones ahora pueden registrarse y crear sus propias bases de datos aisladas.
