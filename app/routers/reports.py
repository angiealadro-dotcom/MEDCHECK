from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from app.models.checklist import ChecklistSummary
from app.services.snowflake_service import SnowflakeService
from app.services.reporting_service import ReportingService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    area: Optional[str] = None,
    periodo: Optional[str] = "7d"
):
    """
    Dashboard principal de reportes
    """
    current_user = None

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

    # Por ahora retornar datos vacíos
    entries = []
    summary = {}
    
    return templates.TemplateResponse(
        "reports_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "entries": entries,
            "summary": summary,
            "area_filtrada": area,
            "periodo": periodo
        }
    )

@router.get("/summary", response_model=ChecklistSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener resumen de cumplimiento
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver el resumen"
        )

    # Si no es admin y no especificó área, usar su área asignada
    if current_user.role != "admin" and not area:
        area = current_user.area

    summary = await SnowflakeService.get_cumplimiento_summary()
    return summary

@router.get("/anomalies")
async def get_anomalies(
    current_user: User = Depends(get_current_user),
    conn = Depends(get_snowflake_connection)
):
    """
    Detectar anomalías en el cumplimiento
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver anomalías"
        )

    # Implementar lógica de detección de anomalías
    cursor = conn.cursor()
    try:
        cursor.execute("""
        WITH promedios AS (
            SELECT area, 
                   AVG(CASE WHEN cumple THEN 1 ELSE 0 END) as promedio_cumplimiento
            FROM checklist_entries
            WHERE fecha_hora >= DATEADD(day, -30, CURRENT_TIMESTAMP())
            GROUP BY area
        )
        SELECT 
            c.area,
            c.protocolo_etapa,
            COUNT(*) as total_registros,
            AVG(CASE WHEN c.cumple THEN 1 ELSE 0 END) as cumplimiento_actual,
            p.promedio_cumplimiento as promedio_historico
        FROM checklist_entries c
        JOIN promedios p ON c.area = p.area
        WHERE fecha_hora >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        GROUP BY c.area, c.protocolo_etapa, p.promedio_cumplimiento
        HAVING cumplimiento_actual < (promedio_historico * 0.8)  -- 20% bajo el promedio
        ORDER BY (promedio_historico - cumplimiento_actual) DESC
        LIMIT 10
        """)
        
        columns = [desc[0] for desc in cursor.description]
        anomalies = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"anomalies": anomalies}
        
    finally:
        cursor.close()

@router.get("/critical-items")
async def get_critical_items(
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener items críticos que requieren atención inmediata
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver items críticos"
        )
    
    # Si no es admin y no especificó área, usar su área asignada
    if current_user.role != "admin" and not area:
        area = current_user.area

    # Si no se especifican fechas, usar últimos 7 días
    if not desde:
        desde = datetime.now() - timedelta(days=7)
    if not hasta:
        hasta = datetime.now()

    reporting_service = ReportingService()
    critical_items = await reporting_service.get_critical_items(area, desde, hasta)
    return critical_items

@router.get("/turnos-comparison")
async def get_turnos_comparison(
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None,
    periodo: Optional[str] = "7d"
):
    """
    Obtener comparación de cumplimiento entre turnos
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver comparación de turnos"
        )

    # Si no es admin y no especificó área, usar su área asignada
    if current_user.role != "admin" and not area:
        area = current_user.area

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

    reporting_service = ReportingService()
    comparison = await reporting_service.get_turno_comparison(area, desde, hasta)
    return comparison

@router.get("/compliance-trends")
async def get_compliance_trends(
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None,
    periodo: Optional[str] = "30d",
    agrupacion: Optional[str] = "day"
):
    """
    Obtener tendencias de cumplimiento en el tiempo
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver tendencias"
        )

    # Si no es admin y no especificó área, usar su área asignada
    if current_user.role != "admin" and not area:
        area = current_user.area

    # Calcular fechas según periodo
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=30)

    reporting_service = ReportingService()
    trends = await reporting_service.get_compliance_trends(area, desde, hasta, agrupacion)
    return trends