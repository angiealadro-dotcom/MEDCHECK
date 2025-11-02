"""
Router de alertas simplificado para SQLite
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.auth.users import get_current_active_user
from app.models.user import User
from app.db.database import get_db
from app.services.alert_service_sqlite import AlertService

templates = Jinja2Templates(directory="templates")
router = APIRouter()
alert_service = AlertService()

@router.get("/critical")
async def get_critical_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    area: Optional[str] = None
):
    """
    Obtener alertas críticas actuales
    """
    # Si no es admin, solo puede ver alertas de su área
    if not current_user.is_admin and area is None:
        area = getattr(current_user, 'area', None)
        
    alerts = alert_service.get_critical_alerts(db, area)
    return {"alerts": alerts}

@router.get("/config", response_class=HTMLResponse)
async def get_alert_config_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Página de configuración de alertas
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a la configuración"
        )
    
    # Obtener configuración actual
    config = alert_service.get_config(db)
    
    # Obtener alertas recientes para mostrar
    alertas_recientes = alert_service.get_critical_alerts(db, None)
    
    return templates.TemplateResponse(
        "alert_config.html",
        {
            "request": request,
            "current_user": current_user,
            "config": config,
            "alert_logs": [],  # TODO: Implementar log de alertas
            "alerts": alertas_recientes[:10]  # Últimas 10 alertas
        }
    )

@router.get("/configs")
async def get_alert_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener configuración de alertas (API)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver configuraciones"
        )
    
    config = alert_service.get_config(db)
    return config

@router.post("/configs")
async def save_alert_config(
    config: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Guardar configuración de alertas
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden modificar configuraciones"
        )
    
    saved_config = alert_service.save_config(db, config)
    return saved_config

@router.post("/test")
async def test_alert(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Simular envío de alerta de prueba
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden enviar alertas de prueba"
        )
    
    return {
        "message": f"Alerta de prueba simulada para {email}",
        "note": "SMTP no configurado - esta es una simulación"
    }
