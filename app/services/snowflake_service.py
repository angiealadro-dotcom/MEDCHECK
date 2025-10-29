from typing import List, Optional
from datetime import datetime
from app.db.snowflake_db import get_snowflake_cursor
from app.models.schemas import ChecklistEntry, ChecklistForm

class SnowflakeService:
    @staticmethod
    async def create_checklist_entries(form: ChecklistForm, usuario: str) -> bool:
        cursor = next(get_snowflake_cursor())
        try:
            # Procesar los items del formulario
            for etapa, items in form.items.items():
                for item_name, cumple in items.items():
                    cursor.execute("""
                    INSERT INTO checklist_entries (
                        protocolo_etapa, item, cumple, observaciones,
                        usuario, area, turno
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        etapa,
                        f"{etapa}_{item_name}",
                        cumple,
                        form.observaciones,
                        usuario,
                        form.area,
                        form.turno
                    ))
            
            cursor.connection.commit()
            return True
        except Exception as e:
            print(f"Error al crear entradas de checklist: {e}")
            cursor.connection.rollback()
            return False

    @staticmethod
    async def get_checklist_entries(
        area: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> List[dict]:
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
            SELECT * FROM checklist_entries
            WHERE {where_sql}
            ORDER BY fecha_hora DESC
            """, params)
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error al obtener entradas de checklist: {e}")
            return []

    @staticmethod
    async def get_cumplimiento_summary() -> dict:
        cursor = next(get_snowflake_cursor())
        try:
            cursor.execute("""
            SELECT 
                COUNT(*) as total_registros,
                SUM(CASE WHEN cumple THEN 1 ELSE 0 END) as registros_cumplidos,
                (registros_cumplidos::FLOAT / total_registros) * 100 as porcentaje_cumplimiento,
                COUNT(DISTINCT area) as total_areas,
                COUNT(DISTINCT protocolo_etapa) as total_etapas
            FROM checklist_entries
            """)
            
            result = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
            
        except Exception as e:
            print(f"Error al obtener resumen de cumplimiento: {e}")
            return {
                "total_registros": 0,
                "registros_cumplidos": 0,
                "porcentaje_cumplimiento": 0,
                "total_areas": 0,
                "total_etapas": 0
            }