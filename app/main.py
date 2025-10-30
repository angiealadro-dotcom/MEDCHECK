from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.db.database import create_tables
from app.routers import auth_simple, checklist, reports
from app.config import settings

# Crear la aplicación
app = FastAPI(
    title=settings.app_name,
    description="Sistema de verificación de buenas prácticas en la administración de medicamentos",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de templates
templates = Jinja2Templates(directory="templates")

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth_simple.router)
app.include_router(checklist.router, prefix="/checklist", tags=["checklist"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# Página de login
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

# Inicialización de la base de datos
@app.on_event("startup")
async def startup_event():
    create_tables()
    print(f"✅ {settings.app_name} iniciado correctamente")
    print(f"📊 Base de datos: {settings.database_url}")
    print(f"🌍 Entorno: {settings.environment}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}

# Ruta de diagnóstico para listar endpoints disponibles
@app.get("/debug/routes")
async def debug_routes():
    try:
        return [
            {"path": r.path, "name": getattr(r, "name", None)}
            for r in app.routes
        ]
    except Exception as e:
        return {"error": str(e)}
