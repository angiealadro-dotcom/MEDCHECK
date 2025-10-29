from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Optional
from datetime import datetime
from app.models.schemas import ChecklistEntry, ChecklistForm
from app.services.snowflake_service import SnowflakeService
from app.security.auth_deps import get_current_user
from app.models.auth import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/new", response_class=HTMLResponse)
async def new_checklist_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Mostrar formulario para nueva lista de cotejo
    """
    return templates.TemplateResponse(
        "checklist_form.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/")
async def create_checklist_entry(
    entry: ChecklistForm,
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo registro de lista de cotejo
    """
    # Verificar permisos basados en rol
    if current_user.role not in ["enfermero", "supervisor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear registros"
        )

    success = await SnowflakeService.create_checklist_entries(entry, current_user.username)
    if success:
        return {"status": "success", "message": "Registros creados correctamente"}
    raise HTTPException(status_code=400, detail="Error al crear registros")

@router.get("/history", response_class=HTMLResponse)
async def get_checklist_history(
    request: Request,
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Mostrar historial de listas de cotejo
    """
    # Si no es admin/supervisor, solo puede ver su área
    if current_user.role not in ["admin", "supervisor"]:
        area = current_user.area

    entries = await SnowflakeService.get_checklist_entries(area, desde, hasta)
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