from datetime import datetime, timedelta
from typing import List, Optional
from app.models.audit import AuditLog
from app.db.snowflake_db import get_snowflake_cursor

class AuditService:
    @staticmethod
    async def create_audit_log(log: AuditLog):
        """
        Registra un evento de auditoría en Snowflake
        """
        cursor = next(get_snowflake_cursor())
        try:
            cursor.execute("""
                INSERT INTO audit_logs (
                    event_type, username, ip_address, timestamp,
                    details, area, role, status, user_agent, session_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log.event_type,
                log.username,
                log.ip_address,
                log.timestamp,
                log.details,
                log.area,
                log.role,
                log.status,
                log.user_agent,
                log.session_id
            ))
            cursor.connection.commit()
        except Exception as e:
            print(f"Error registrando auditoría: {e}")
            cursor.connection.rollback()

    @staticmethod
    async def get_security_events(
        username: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Obtiene eventos de seguridad con filtros
        """
        cursor = next(get_snowflake_cursor())
        try:
            where_clauses = []
            params = []
            
            if username:
                where_clauses.append("username = %s")
                params.append(username)
            
            if event_type:
                where_clauses.append("event_type = %s")
                params.append(event_type)
            
            if status:
                where_clauses.append("status = %s")
                params.append(status)
            
            if desde:
                where_clauses.append("timestamp >= %s")
                params.append(desde)
            
            if hasta:
                where_clauses.append("timestamp <= %s")
                params.append(hasta)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            cursor.execute(f"""
                SELECT * FROM audit_logs
                WHERE {where_sql}
                ORDER BY timestamp DESC
                LIMIT {limit}
            """, params)
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error obteniendo eventos de auditoría: {e}")
            return []

    @staticmethod
    async def get_security_summary() -> dict:
        """
        Obtiene resumen de eventos de seguridad
        """
        cursor = next(get_snowflake_cursor())
        try:
            # Últimas 24 horas
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failed_events,
                    COUNT(DISTINCT username) as unique_users,
                    COUNT(DISTINCT ip_address) as unique_ips,
                    COUNT(CASE WHEN event_type = 'failed_login' THEN 1 END) as failed_logins,
                    COUNT(CASE WHEN event_type = 'account_locked' THEN 1 END) as account_lockouts
                FROM audit_logs
                WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
            """)
            
            daily_summary = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            
            # Tendencias por hora
            cursor.execute("""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour,
                    COUNT(*) as events,
                    COUNT(CASE WHEN status = 'failure' THEN 1 END) as failures
                FROM audit_logs
                WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
                GROUP BY hour
                ORDER BY hour
            """)
            
            hourly_trends = [dict(zip([desc[0] for desc in cursor.description], row))
                           for row in cursor.fetchall()]
            
            return {
                "daily_summary": daily_summary,
                "hourly_trends": hourly_trends
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen de seguridad: {e}")
            return {
                "daily_summary": {},
                "hourly_trends": []
            }