# MedCheck - Sistema de Verificación de Medicación

Sistema web para gestionar protocolos y listas de cotejo en la administración de medicamentos hospitalarios.

## Características

- ✅ Registro de verificaciones por etapa del protocolo
- 📊 Reportes de cumplimiento
- 🔍 Detección de anomalías
- 📱 Interfaz web responsive
- 🔐 Autenticación de usuarios
- ⚡ API REST
- 🗄️ Almacenamiento en Snowflake

## Requisitos

- Python 3.8+
- Cuenta de Snowflake
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPO]
cd medcheck
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de Snowflake
```

## Uso

1. Iniciar el servidor:
```bash
uvicorn app.main:app --reload
```

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