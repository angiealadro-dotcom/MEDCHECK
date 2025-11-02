from fastapi import APIRouter, Request, Depends, HTTPException
import os
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from datetime import datetime, timedelta
from app.services.snowflake_service import SnowflakeService
from app.services.reporting_service import ReportingService
from app.services.export_service import ExportService
from app.services.voice_service import VoiceService
from app.auth.users import get_current_active_user
from app.models.user import User
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.checklist_sqlite_service import get_recent_entries
from app.models.checklist_entry import ChecklistEntrySQL
from sqlalchemy import func
import io

router = APIRouter()
templates = Jinja2Templates(directory="templates")
export_service = ExportService()
voice_service = VoiceService()

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
    
    # Determinar si la voz está habilitada leyendo env en tiempo de petición
    voice_key = os.getenv("ELEVENLABS_API_KEY") or voice_service.settings.elevenlabs_api_key
    voice_enabled = bool(voice_key)

    return templates.TemplateResponse(
        "reports_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "entries": entries[:50],  # Limitar a 50 para la tabla
            "summary": summary,
            "area_filtrada": area,
            "periodo": periodo,
            "areas_disponibles": areas_lista,
            # Mostrar/ocultar botón de voz según disponibilidad de API Key
            "voice_enabled": voice_enabled
        }
    )

@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener resumen de cumplimiento con datos reales
    """
    query = db.query(ChecklistEntrySQL)
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    if desde:
        query = query.filter(ChecklistEntrySQL.fecha_hora >= desde)
    if hasta:
        query = query.filter(ChecklistEntrySQL.fecha_hora <= hasta)
    
    entries = query.all()
    total = len(entries)
    cumple_count = sum(1 for e in entries if e.cumple)
    
    # Agrupaciones
    por_area = {}
    por_turno = {}
    por_etapa = {}
    
    for entry in entries:
        # Por área
        if entry.area not in por_area:
            por_area[entry.area] = {"total": 0, "cumple": 0}
        por_area[entry.area]["total"] += 1
        if entry.cumple:
            por_area[entry.area]["cumple"] += 1
        
        # Por turno
        if entry.turno not in por_turno:
            por_turno[entry.turno] = {"total": 0, "cumple": 0}
        por_turno[entry.turno]["total"] += 1
        if entry.cumple:
            por_turno[entry.turno]["cumple"] += 1
        
        # Por etapa
        if entry.protocolo_etapa not in por_etapa:
            por_etapa[entry.protocolo_etapa] = {"total": 0, "cumple": 0}
        por_etapa[entry.protocolo_etapa]["total"] += 1
        if entry.cumple:
            por_etapa[entry.protocolo_etapa]["cumple"] += 1
    
    # Calcular porcentajes
    for area_key in por_area:
        por_area[area_key]["porcentaje"] = (por_area[area_key]["cumple"] / por_area[area_key]["total"] * 100) if por_area[area_key]["total"] > 0 else 0
    
    for turno_key in por_turno:
        por_turno[turno_key]["porcentaje"] = (por_turno[turno_key]["cumple"] / por_turno[turno_key]["total"] * 100) if por_turno[turno_key]["total"] > 0 else 0
    
    for etapa_key in por_etapa:
        por_etapa[etapa_key]["porcentaje"] = (por_etapa[etapa_key]["cumple"] / por_etapa[etapa_key]["total"] * 100) if por_etapa[etapa_key]["total"] > 0 else 0
    
    return {
        "total_registros": total,
        "total_cumple": cumple_count,
        "porcentaje_cumplimiento": (cumple_count / total * 100) if total > 0 else 0,
        "por_area": por_area,
        "por_turno": por_turno,
        "por_etapa": por_etapa
    }

@router.get("/anomalies")
async def get_anomalies(db: Session = Depends(get_db)):
    """
    Detectar anomalías en el cumplimiento (patrones inusuales)
    """
    # Obtener datos de los últimos 30 días
    desde = datetime.now() - timedelta(days=30)
    entries = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    ).all()
    
    anomalies = []
    
    # Detectar áreas con cumplimiento < 50%
    area_stats = {}
    for entry in entries:
        if entry.area not in area_stats:
            area_stats[entry.area] = {"total": 0, "cumple": 0}
        area_stats[entry.area]["total"] += 1
        if entry.cumple:
            area_stats[entry.area]["cumple"] += 1
    
    for area, stats in area_stats.items():
        cumplimiento = (stats["cumple"] / stats["total"] * 100) if stats["total"] > 0 else 0
        if cumplimiento < 50:
            anomalies.append({
                "tipo": "cumplimiento_critico",
                "area": area,
                "descripcion": f"Cumplimiento crítico en {area}: {cumplimiento:.1f}%",
                "severidad": "alta",
                "valor": cumplimiento
            })
        elif cumplimiento < 70:
            anomalies.append({
                "tipo": "cumplimiento_bajo",
                "area": area,
                "descripcion": f"Cumplimiento bajo en {area}: {cumplimiento:.1f}%",
                "severidad": "media",
                "valor": cumplimiento
            })
    
    return {"anomalies": anomalies}

@router.get("/critical-items")
async def get_critical_items(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
    """
    Obtener items críticos (registros que no cumplen)
    """
    query = db.query(ChecklistEntrySQL).filter(ChecklistEntrySQL.cumple == False)
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    if desde:
        query = query.filter(ChecklistEntrySQL.fecha_hora >= desde)
    if hasta:
        query = query.filter(ChecklistEntrySQL.fecha_hora <= hasta)
    
    critical_entries = query.order_by(ChecklistEntrySQL.fecha_hora.desc()).limit(100).all()
    
    return [{
        "id": entry.id,
        "fecha_hora": entry.fecha_hora.isoformat(),
        "area": entry.area,
        "turno": entry.turno,
        "protocolo_etapa": entry.protocolo_etapa,
        "observaciones": entry.observaciones
    } for entry in critical_entries]

@router.get("/turnos-comparison")
async def get_turnos_comparison(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    periodo: Optional[str] = "7d"
):
    """
    Obtener comparación de cumplimiento entre turnos
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

    query = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    )
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    
    entries = query.all()
    
    turnos_stats = {}
    for entry in entries:
        if entry.turno not in turnos_stats:
            turnos_stats[entry.turno] = {"total": 0, "cumple": 0}
        turnos_stats[entry.turno]["total"] += 1
        if entry.cumple:
            turnos_stats[entry.turno]["cumple"] += 1
    
    # Calcular porcentajes
    for turno in turnos_stats:
        turnos_stats[turno]["porcentaje"] = (
            turnos_stats[turno]["cumple"] / turnos_stats[turno]["total"] * 100
        ) if turnos_stats[turno]["total"] > 0 else 0
    
    return {
        "periodo": periodo,
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "turnos": turnos_stats
    }

@router.get("/voice-status")
async def voice_status():
    """Pequeño endpoint de diagnóstico (no expone la clave)"""
    has_key = bool(os.getenv("ELEVENLABS_API_KEY") or voice_service.settings.elevenlabs_api_key)
    return {"enabled": has_key}

@router.get("/compliance-trends")
async def get_compliance_trends(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    periodo: Optional[str] = "30d",
    agrupacion: Optional[str] = "day"
):
    """
    Obtener tendencias de cumplimiento en el tiempo
    """
    # Calcular rango de fechas
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=30)
    
    query = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    )
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    
    entries = query.order_by(ChecklistEntrySQL.fecha_hora).all()
    
    # Agrupar por día
    tendencias = {}
    for entry in entries:
        fecha_key = entry.fecha_hora.strftime("%Y-%m-%d")
        if fecha_key not in tendencias:
            tendencias[fecha_key] = {"total": 0, "cumple": 0}
        tendencias[fecha_key]["total"] += 1
        if entry.cumple:
            tendencias[fecha_key]["cumple"] += 1
    
    # Convertir a lista ordenada con porcentajes
    resultado = []
    for fecha, stats in sorted(tendencias.items()):
        resultado.append({
            "fecha": fecha,
            "total": stats["total"],
            "cumple": stats["cumple"],
            "porcentaje": (stats["cumple"] / stats["total"] * 100) if stats["total"] > 0 else 0
        })
    
    return resultado

@router.get("/export/pdf")
async def export_report_to_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    area: Optional[str] = None,
    desde: Optional[datetime] = None,
    hasta: Optional[datetime] = None
):
        """
        Exportar reporte de cumplimiento a PDF
        """
        # Obtener datos del resumen
        query = db.query(ChecklistEntrySQL)
    
        if area:
            query = query.filter(ChecklistEntrySQL.area == area)
        if desde:
            query = query.filter(ChecklistEntrySQL.fecha_hora >= desde)
        if hasta:
            query = query.filter(ChecklistEntrySQL.fecha_hora <= hasta)
    
        entries = query.all()
        total = len(entries)
        cumple_count = sum(1 for e in entries if e.cumple)
    
        # Calcular por área
        por_area = {}
        for entry in entries:
            if entry.area not in por_area:
                por_area[entry.area] = {"total": 0, "cumple": 0}
            por_area[entry.area]["total"] += 1
            if entry.cumple:
                por_area[entry.area]["cumple"] += 1
    
        for area_key in por_area:
            por_area[area_key]["porcentaje"] = (
                por_area[area_key]["cumple"] / por_area[area_key]["total"] * 100
            ) if por_area[area_key]["total"] > 0 else 0
    
        summary = {
            "total_registros": total,
            "total_cumple": cumple_count,
            "porcentaje_cumplimiento": (cumple_count / total * 100) if total > 0 else 0,
            "por_area": por_area
        }
    
        # Generar PDF
        try:
            pdf_bytes = export_service.export_report_to_pdf(summary)
        
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"medcheck_reporte_{timestamp}.pdf"
        
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al generar PDF: {str(e)}"
            )

@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    periodo: Optional[str] = "7d",
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener recomendaciones inteligentes basadas en el cumplimiento
    """
    # Calcular rango de fechas
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=7)
    
    # Consultar datos
    query = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    )
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    
    entries = query.all()
    
    # Calcular resumen
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
    
    summary = {
        "total_items": total_items,
        "items_cumplidos": items_cumplidos,
        "porcentaje_cumplimiento": porcentaje_cumplimiento,
        "cumplimiento_por_etapa": cumplimiento_por_etapa
    }
    
    # Generar recomendaciones
    recomendaciones = voice_service.get_recommendations(summary)
    
    return {"recomendaciones": recomendaciones, "summary": summary}

@router.get("/voice-summary")
async def get_voice_summary(
    db: Session = Depends(get_db),
    area: Optional[str] = None,
    periodo: Optional[str] = "7d",
    current_user: User = Depends(get_current_active_user)
):
    """
    Generar audio del resumen de reportes usando ElevenLabs
    """
    # Calcular rango de fechas
    hasta = datetime.now()
    if periodo == "7d":
        desde = hasta - timedelta(days=7)
    elif periodo == "30d":
        desde = hasta - timedelta(days=30)
    elif periodo == "90d":
        desde = hasta - timedelta(days=90)
    else:
        desde = hasta - timedelta(days=7)
    
    # Consultar datos
    query = db.query(ChecklistEntrySQL).filter(
        ChecklistEntrySQL.fecha_hora >= desde
    )
    
    if area:
        query = query.filter(ChecklistEntrySQL.area == area)
    
    entries = query.all()
    
    # Calcular resumen
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
    
    summary = {
        "total_items": total_items,
        "items_cumplidos": items_cumplidos,
        "porcentaje_cumplimiento": porcentaje_cumplimiento,
        "cumplimiento_por_etapa": cumplimiento_por_etapa
    }
    
    # Generar audio
    audio_bytes = voice_service.generate_report_speech(summary)
    
    if audio_bytes:
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=reporte_voz.mp3"}
        )
    else:
        raise HTTPException(
            status_code=503,
            detail=(
                "Servicio de voz no disponible. Verifica ELEVENLABS_API_KEY en .env "
                "y que tu clave tenga el permiso 'text_to_speech' habilitado en ElevenLabs."
            )
        )