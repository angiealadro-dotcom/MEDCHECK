from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.db.snowflake_db import get_snowflake_cursor

class ReportingService:
    @staticmethod
    async def get_compliance_summary(
        area: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict:
        """
        Obtiene resumen general de cumplimiento
        """
        cursor = next(get_snowflake_cursor())
        try:
            where_clauses = []
            params = []
            
            if area:
                where_clauses.append("area = %s")
                params.append(area)
            
            if desde:
                where_clauses.append("fecha_hora >= %s")
                params.append(desde)
            
            if hasta:
                where_clauses.append("fecha_hora <= %s")
                params.append(hasta)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Resumen general
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_registros,
                    SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                    COUNT(DISTINCT area) as total_areas,
                    COUNT(DISTINCT protocolo_etapa) as total_etapas,
                    COUNT(DISTINCT usuario) as total_usuarios,
                    AVG(CASE WHEN cumple THEN 1 ELSE 0 END) * 100 as porcentaje_cumplimiento
                FROM checklist_entries
                WHERE {where_sql}
            """, params)
            
            summary = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            
            # Cumplimiento por área
            cursor.execute(f"""
                SELECT 
                    area,
                    COUNT(*) as total_registros,
                    SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                    (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
                FROM checklist_entries
                WHERE {where_sql}
                GROUP BY area
                ORDER BY porcentaje_cumplimiento DESC
            """, params)
            
            areas_cumplimiento = [dict(zip([desc[0] for desc in cursor.description], row))
                                for row in cursor.fetchall()]
            
            # Cumplimiento por etapa
            cursor.execute(f"""
                SELECT 
                    protocolo_etapa,
                    COUNT(*) as total_registros,
                    SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                    (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
                FROM checklist_entries
                WHERE {where_sql}
                GROUP BY protocolo_etapa
                ORDER BY porcentaje_cumplimiento DESC
            """, params)
            
            etapas_cumplimiento = [dict(zip([desc[0] for desc in cursor.description], row))
                                 for row in cursor.fetchall()]
            
            # Tendencia diaria
            cursor.execute(f"""
                SELECT 
                    DATE(fecha_hora) as fecha,
                    COUNT(*) as total_registros,
                    SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                    (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
                FROM checklist_entries
                WHERE {where_sql}
                GROUP BY fecha
                ORDER BY fecha DESC
                LIMIT 30
            """, params)
            
            tendencia_diaria = [dict(zip([desc[0] for desc in cursor.description], row))
                              for row in cursor.fetchall()]
            
            return {
                "resumen": summary,
                "areas": areas_cumplimiento,
                "etapas": etapas_cumplimiento,
                "tendencia": tendencia_diaria
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen de cumplimiento: {e}")
            return {
                "resumen": {},
                "areas": [],
                "etapas": [],
                "tendencia": []
            }

    @staticmethod
    async def get_critical_items(
        umbral_cumplimiento: float = 80.0,
        area: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Identifica items críticos con bajo cumplimiento
        """
        cursor = next(get_snowflake_cursor())
        try:
            where_clauses = []
            params = []
            
            if area:
                where_clauses.append("area = %s")
                params.append(area)
            
            if desde:
                where_clauses.append("fecha_hora >= %s")
                params.append(desde)
            
            if hasta:
                where_clauses.append("fecha_hora <= %s")
                params.append(hasta)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            cursor.execute(f"""
                WITH item_stats AS (
                    SELECT 
                        area,
                        protocolo_etapa,
                        item,
                        COUNT(*) as total_registros,
                        SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                        (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
                    FROM checklist_entries
                    WHERE {where_sql}
                    GROUP BY area, protocolo_etapa, item
                    HAVING COUNT(*) >= 5  -- Mínimo de registros para considerar
                )
                SELECT *
                FROM item_stats
                WHERE porcentaje_cumplimiento < %s
                ORDER BY porcentaje_cumplimiento ASC
                LIMIT 10
            """, params + [umbral_cumplimiento])
            
            return [dict(zip([desc[0] for desc in cursor.description], row))
                    for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error obteniendo items críticos: {e}")
            return []

    @staticmethod
    async def get_turno_comparison(
        area: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Compara cumplimiento entre turnos
        """
        cursor = next(get_snowflake_cursor())
        try:
            where_clauses = []
            params = []
            
            if area:
                where_clauses.append("area = %s")
                params.append(area)
            
            if desde:
                where_clauses.append("fecha_hora >= %s")
                params.append(desde)
            
            if hasta:
                where_clauses.append("fecha_hora <= %s")
                params.append(hasta)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            cursor.execute(f"""
                SELECT 
                    turno,
                    area,
                    COUNT(*) as total_registros,
                    SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                    (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento
                FROM checklist_entries
                WHERE {where_sql}
                GROUP BY turno, area
                ORDER BY area, turno
            """, params)
            
            return [dict(zip([desc[0] for desc in cursor.description], row))
                    for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error obteniendo comparación de turnos: {e}")
            return []