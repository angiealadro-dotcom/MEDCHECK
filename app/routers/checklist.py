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
from app.auth.users import get_current_active_user
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/new", response_class=HTMLResponse)
async def new_checklist_form(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Mostrar formulario para nueva lista de cotejo (requiere login)
    """
    return templates.TemplateResponse(
        "checklist_form.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/")
async def create_checklist_entry(
    entry: ChecklistForm, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crear un nuevo registro de lista de cotejo (requiere login)
    """
    # Guardar en SQLite con el usuario autenticado
    created = create_entries_from_form(db, entry, username=current_user.username)
    return {
        "status": "success",
        "message": f"{len(created)} registros creados correctamente",
        "count": len(created),
        "usuario": current_user.username
    }

@router.get("/history", response_class=HTMLResponse)
async def get_checklist_history(
    request: Request,
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mostrar historial de listas de cotejo (requiere login)
    """
    # Cargar últimos registros desde SQLite
    entries = get_recent_entries(db, limit=200)
    
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener resumen de cumplimiento
    """
    # Solo admin puede ver el resumen completo
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver el resumen general"
        )
    return await SnowflakeService.get_cumplimiento_summary()