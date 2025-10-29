from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from typing import Optional
from app.models.auth import User
from app.routers.auth import get_current_user
from app.services.audit_service import AuditService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def security_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard de seguridad - solo para administradores
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder al dashboard de seguridad"
        )
    
    summary = await AuditService.get_security_summary()
    events = await AuditService.get_security_events(limit=50)
    
    return templates.TemplateResponse(
        "security_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "summary": summary,
            "events": events
        }
    )

@router.get("/events")
async def get_security_events(
    current_user: User = Depends(get_current_user),
    username: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    periodo: str = "24h"
):
    """
    Obtener eventos de seguridad filtrados
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver eventos de seguridad"
        )
    
    # Calcular rango de fechas según periodo
    hasta = datetime.utcnow()
    if periodo == "24h":
        desde = hasta - timedelta(hours=24)
    elif periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    else:
        desde = hasta - timedelta(hours=24)
    
    events = await AuditService.get_security_events(
        username=username,
        event_type=event_type,
        status=status,
        desde=desde,
        hasta=hasta
    )
    
    summary = await AuditService.get_security_summary()
    
    return {
        "events": events,
        "summary": summary
    }