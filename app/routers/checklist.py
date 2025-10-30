from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Optional
from datetime import datetime
from app.models.schemas import ChecklistEntry, ChecklistForm
from app.services.snowflake_service import SnowflakeService
from app.services.checklist_sqlite_service import create_entries_from_form, get_recent_entries
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.security.auth_deps import get_current_user
from app.models.auth import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/new", response_class=HTMLResponse)
async def new_checklist_form(
    request: Request
):
    """
    Mostrar formulario para nueva lista de cotejo
    """
    current_user = None
    return templates.TemplateResponse(
        "checklist_form.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/")
async def create_checklist_entry(entry: ChecklistForm, db: Session = Depends(get_db)):
    """
    Crear un nuevo registro de lista de cotejo (modo demo)
    """
    # Guardar en SQLite (modo demo)
    created = create_entries_from_form(db, entry, username="demo")
    return {
        "status": "success",
        "message": f"{len(created)} registros creados correctamente",
        "count": len(created)
    }

@router.get("/history", response_class=HTMLResponse)
async def get_checklist_history(
    request: Request,
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Mostrar historial de listas de cotejo
    """
    # Cargar últimos registros desde SQLite (modo demo)
    entries = get_recent_entries(db, limit=200)
    current_user = None
    
    return templates.TemplateResponse(
        "checklist_history.html",
        {
            "request": request, 
            "entries": entries,
            "current_user": current_user
        }
    )

@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener resumen de cumplimiento
    """
    # Solo admin y supervisores pueden ver el resumen completo
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver el resumen general"
        )
    return await SnowflakeService.get_cumplimiento_summary()