"""
Servicio de alertas simplificado para SQLite
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.checklist_entry import ChecklistEntrySQL
from app.models.user import User

class AlertService:
    """Servicio simplificado de alertas para SQLite"""
    
    def get_critical_alerts(self, db: Session, area: Optional[str] = None) -> List[dict]:
        """
        Obtener alertas críticas basadas en umbrales de cumplimiento
        """
        # Obtener registros de las últimas 24 horas
        desde = datetime.now() - timedelta(hours=24)
        
        query = db.query(ChecklistEntrySQL).filter(
            ChecklistEntrySQL.fecha_hora >= desde
        )
        
        if area:
            query = query.filter(ChecklistEntrySQL.area == area)
        
        entries = query.all()
        
        # Agrupar por área y etapa
        agrupado = {}
        for entry in entries:
            key = f"{entry.area}|{entry.protocolo_etapa}"
            if key not in agrupado:
                agrupado[key] = {
                    "area": entry.area,
                    "protocolo_etapa": entry.protocolo_etapa,
                    "total": 0,
                    "cumple": 0,
                    "ultima_revision": entry.fecha_hora
                }
            
            agrupado[key]["total"] += 1
            if entry.cumple:
                agrupado[key]["cumple"] += 1
            
            if entry.fecha_hora > agrupado[key]["ultima_revision"]:
                agrupado[key]["ultima_revision"] = entry.fecha_hora
        
        # Filtrar alertas críticas (cumplimiento < 70%)
        alertas = []
        for stats in agrupado.values():
            cumplimiento = (stats["cumple"] / stats["total"] * 100) if stats["total"] > 0 else 0
            if cumplimiento < 70:
                alertas.append({
                    **stats,
                    "cumplimiento": cumplimiento,
                    "severidad": "critica" if cumplimiento < 50 else "alta"
                })
        
        return sorted(alertas, key=lambda x: x["cumplimiento"])
    
    def get_config(self, db: Session) -> dict:
        """
        Obtener configuración de alertas
        """
        # Configuración por defecto
        return {
            "umbral_critico": 70.0,
            "umbral_advertencia": 85.0,
            "intervalo_horas": 24,
            "activo": True
        }
    
    def save_config(self, db: Session, config: dict) -> dict:
        """
        Guardar configuración de alertas
        """
        # Por ahora retornamos la config que recibimos
        # TODO: Implementar persistencia en SQLite
        return config
