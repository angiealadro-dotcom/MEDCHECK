from fastapi import APIRouter, Request, Depends
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from app.services.snowflake_service import SnowflakeService
from app.services.reporting_service import ReportingService
from app.auth.users import get_current_active_user
from app.models.user import User
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.checklist_sqlite_service import get_recent_entries
from app.models.checklist_entry import ChecklistEntrySQL
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    area: Optional[str] = None,
    periodo: Optional[str] = "7d",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard principal de reportes (requiere login)
    """
    # Calcular rango de fechas según periodo
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=7)

    # Consultar datos reales desde SQLite
    query = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    )
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    
    entries = query.all()
    
    # Calcular estadísticas
    total_items = len(entries)
    items_cumplidos = len([e for e in entries if e.cumple])
    porcentaje_cumplimiento = round((items_cumplidos / total_items * 100) if total_items > 0 else 0, 1)
    
    # Agrupar por etapa
    cumplimiento_por_etapa = {}
    for etapa in ["prescripción", "preparación", "administración"]:
        items_etapa = [e for e in entries if e.protocolo_etapa == etapa]
        cumplidos_etapa = len([e for e in items_etapa if e.cumple])
        total_etapa = len(items_etapa)
        cumplimiento_por_etapa[etapa] = {
            "total": total_etapa,
            "cumplidos": cumplidos_etapa,
            "porcentaje": round((cumplidos_etapa / total_etapa * 100) if total_etapa > 0 else 0, 1)
        }
    
    # Obtener áreas únicas
    areas = db.query(ChecklistEntrySQL.area).distinct().all()
    areas_lista = [a[0] for a in areas if a[0]]
    
    summary = {
        "total_items": total_items,
        "items_cumplidos": items_cumplidos,
        "porcentaje_cumplimiento": porcentaje_cumplimiento,
        "cumplimiento_por_etapa": cumplimiento_por_etapa,
        "periodo_desde": desde.strftime("%Y-%m-%d"),
        "periodo_hasta": hasta.strftime("%Y-%m-%d")
    }
    
    return templates.TemplateResponse(
        "reports_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "entries": entries[:50],  # Limitar a 50 para la tabla
            "summary": summary,
            "area_filtrada": area,
            "periodo": periodo,
            "areas_disponibles": areas_lista
        }
    )

@router.get("/summary")
async def get_summary(
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener resumen de cumplimiento (placeholder sin autenticación)
    """
    # Devolver estructura vacía temporalmente
    return {}

@router.get("/anomalies")
async def get_anomalies():
    """
    Detectar anomalías en el cumplimiento (placeholder sin autenticación)
    """
    return {"anomalies": []}

@router.get("/critical-items")
async def get_critical_items(
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener items críticos (placeholder sin autenticación)
    """
    return []

@router.get("/turnos-comparison")
async def get_turnos_comparison(
    area: Optional[str] = None,
    periodo: Optional[str] = "7d"
):
    """
    Obtener comparación de cumplimiento entre turnos (placeholder)
    """
    # Calcular fechas según periodo
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=7)

    return {}

@router.get("/compliance-trends")
async def get_compliance_trends(
    area: Optional[str] = None,
    periodo: Optional[str] = "30d",
    agrupacion: Optional[str] = "day"
):
    """
    Obtener tendencias de cumplimiento en el tiempo (placeholder)
    """
    return []