from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from app.db.database import create_tables
from app.routers import auth_simple, checklist, reports
from app.routers import alerts_sqlite as alerts
from app.config import settings

# Crear la aplicación
app = FastAPI(
    title=settings.app_name,
    description="Sistema de verificación de buenas prácticas en la administración de medicamentos",
    version="1.0.3"  # Fix para producción
)

# Exception handler para redirigir a login en caso de 401
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Si es un error 401 y la petición espera HTML, redirigir a login
    if exc.status_code == 401:
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return RedirectResponse(url="/login?next=" + str(request.url.path), status_code=302)
    # Para otros casos, retornar el error JSON normal
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
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
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])

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

# Endpoint temporal para crear usuario admin (elimina el existente si hay problemas)
@app.get("/setup-admin")
async def setup_admin(request: Request, force: bool = False, format: str = "json"):
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.auth.users import get_password_hash
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin and not force:
            payload = {
                "status": "already_exists",
                "message": "El usuario admin ya existe. Usa ?force=true para recrearlo",
                "username": existing_admin.username,
                "email": existing_admin.email,
                "hint": "Si tienes problemas de login, visita: /setup-admin?force=true"
            }
            if format == "html":
                return HTMLResponse(f"""
                    <html><body>
                    <h3>Usuario admin ya existe</h3>
                    <pre>{payload}</pre>
                    <a href='/login'>Ir a login</a>
                    </body></html>
                """)
            return payload
        
        # Si force=true, eliminar el admin existente
        if existing_admin:
            db.delete(existing_admin)
            db.commit()
        
        # Crear nuevo usuario admin usando un hash precomputado para evitar
        # cualquier problema del backend bcrypt en tiempo de ejecución
        # Contraseña en texto plano: Admin123!
        hashed_password = "$2b$12$stqmrbQjNtvsb.HqdDcnbeYPo853D3o.N.Lti6dwyQ2YSDn5pKqmS"
        admin = User(
            username="admin",
            email="admin@medcheck.com",
            hashed_password=hashed_password,
            full_name="Administrador del Sistema",
            is_active=True,
            is_admin=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        payload = {
            "status": "success",
            "message": "Usuario administrador creado exitosamente con el fix de bcrypt",
            "username": "admin",
            "password": "Admin123!",
            "email": admin.email,
            "login_url": "/login",
            "recreated": existing_admin is not None
        }
        if format == "html":
            return HTMLResponse(f"""
                <html><body>
                <h3>Administrador creado</h3>
                <pre>{payload}</pre>
                <a href='/login?next=/reports/dashboard'>Ir a login</a>
                </body></html>
            """)
        return payload
        
    except Exception as e:
        db.rollback()
        diag = {
            "status": "error",
            "stage": "db",
            "type": e.__class__.__name__,
            "message": str(e)
        }
        if format == "html":
            return HTMLResponse(f"<pre>{diag}</pre>")
        return diag
    finally:
        db.close()

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
