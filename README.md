# MedCheck - Sistema de Verificación de Medicación

Sistema web para gestionar protocolos y listas de cotejo en la administración de medicamentos hospitalarios.

## Características

- ✅ Registro de verificaciones por etapa del protocolo
- 📊 Reportes de cumplimiento en tiempo real
- 🔍 Detección de anomalías y alertas
- 📱 Interfaz web responsive con PWA
- 🔐 Autenticación segura de usuarios
- ⚡ API REST con FastAPI
- 🗄️ Almacenamiento flexible (SQLite/PostgreSQL/Snowflake)
- 🔔 Notificaciones push y recordatorios
- 🎙️ Asistente de voz (ElevenLabs)

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Cuenta de Snowflake (opcional, para producción)
- API Key de ElevenLabs (opcional, para asistente de voz)

## Instalación Rápida

1. **Clonar el repositorio:**
```bash
git clone https://github.com/angiealadro-dotcom/medcheck.git
cd medcheck
```

2. **Crear un entorno virtual:**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional):**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Editar .env con tus configuraciones personalizadas
```

5. **Inicializar la base de datos:**
```bash
python init_db.py
```

## Uso

### Método 1: Launcher Python (Recomendado)
```bash
python run_dev.py
```

Este script:
- ✅ Verifica dependencias
- ✅ Inicia el servidor con auto-reload
- ✅ Abre automáticamente el navegador
- ✅ Funciona en Windows, Linux y Mac

### Método 2: Comando directo
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

### Método 3: Script Windows
```cmd
.\start_local_server.cmd
```

## Acceso al Sistema

- **URL Principal:** http://127.0.0.1:8002
- **Documentación API:** http://127.0.0.1:8002/docs
- **Health Check:** http://127.0.0.1:8002/health

### Credenciales por Defecto

```
Usuario: admin
Contraseña: Admin123!
```

> ⚠️ **IMPORTANTE:** Cambia estas credenciales en producción

2. Acceder a la documentación de la API:
```
http://localhost:8000/docs
```

## Estructura del Proyecto

```
medcheck/
├── app/
│   ├── main.py           # Aplicación FastAPI
│   ├── routers/          # Endpoints de la API
│   ├── models/           # Modelos Pydantic
│   ├── db/              # Conexión a Snowflake
│   └── auth/            # Autenticación
├── static/              # Archivos estáticos
├── templates/           # Templates Jinja2
├── tests/              # Tests
├── requirements.txt    # Dependencias
└── .env.example       # Template de variables de entorno
```

## Endpoints Principales

- `POST /checklist/`: Crear nuevo registro de verificación
- `GET /checklist/`: Obtener registros con filtros
- `GET /reports/summary`: Resumen de cumplimiento
- `GET /reports/anomalies`: Detección de anomalías
- `POST /auth/token`: Login (obtener token JWT)

## Seguridad

- Autenticación JWT
- Validación de datos con Pydantic
- CORS configurado
- Variables de entorno para secrets

## Contribuir

1. Fork el repositorio
2. Crear rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Siguientes Pasos

- [ ] Implementar frontend con templates
- [ ] Añadir tests
- [ ] Configurar CI/CD
- [ ] Implementar análisis NLP de observaciones
- [ ] Añadir notificaciones
