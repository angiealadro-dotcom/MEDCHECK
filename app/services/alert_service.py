from typing import List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.db.snowflake import get_snowflake_connection
from app.models.auth import User

class AlertService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
    async def get_critical_alerts(self, area: Optional[str] = None) -> List[dict]:
        """
        Obtener alertas críticas basadas en umbrales de cumplimiento
        """
        conn = await get_snowflake_connection()
        cursor = conn.cursor()
        try:
            query = """
            WITH ultimos_registros AS (
                SELECT 
                    area,
                    protocolo_etapa,
                    cumple,
                    fecha_hora,
                    user_id,
                    ROW_NUMBER() OVER (PARTITION BY area, protocolo_etapa ORDER BY fecha_hora DESC) as rn
                FROM checklist_entries
                WHERE fecha_hora >= DATEADD(day, -1, CURRENT_TIMESTAMP())
                {% if area %}
                AND area = %(area)s
                {% endif %}
            )
            SELECT 
                ur.area,
                ur.protocolo_etapa,
                COUNT(*) as total_checks,
                AVG(CASE WHEN ur.cumple THEN 1 ELSE 0 END) as cumplimiento,
                MAX(ur.fecha_hora) as ultima_revision,
                STRING_AGG(DISTINCT u.email) as emails_supervisores
            FROM ultimos_registros ur
            JOIN users u ON u.area = ur.area AND u.role = 'supervisor'
            WHERE ur.rn = 1
            GROUP BY ur.area, ur.protocolo_etapa
            HAVING cumplimiento < 0.7  -- Alertar cuando el cumplimiento es menor al 70%
            ORDER BY cumplimiento ASC
            """
            
            params = {"area": area} if area else {}
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return alerts
            
        finally:
            cursor.close()

    async def send_email_alert(self, recipient: str, subject: str, body: str):
        """
        Enviar alerta por email
        """
        if not all([self.smtp_username, self.smtp_password]):
            raise ValueError("SMTP credentials not configured")
            
        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = recipient
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def process_alerts(self):
        """
        Procesar y enviar alertas según los criterios definidos
        """
        alerts = await self.get_critical_alerts()
        
        for alert in alerts:
            if alert["emails_supervisores"]:
                subject = f"⚠️ Alerta Crítica - {alert['area']} - {alert['protocolo_etapa']}"
                body = f"""
                <h2>Alerta de Cumplimiento Crítico</h2>
                <p><strong>Área:</strong> {alert['area']}</p>
                <p><strong>Etapa:</strong> {alert['protocolo_etapa']}</p>
                <p><strong>Cumplimiento Actual:</strong> {alert['cumplimiento']*100:.1f}%</p>
                <p><strong>Total Revisiones:</strong> {alert['total_checks']}</p>
                <p><strong>Última Revisión:</strong> {alert['ultima_revision'].strftime('%Y-%m-%d %H:%M')}</p>
                <p style="color: red;">El cumplimiento está por debajo del umbral crítico (70%). Se requiere atención inmediata.</p>
                <p><a href="https://medcheck.app/reports/dashboard?area={alert['area']}">Ver Dashboard</a></p>
                """
                
                # Enviar a cada supervisor
                for email in alert["emails_supervisores"].split(","):
                    await self.send_email_alert(email.strip(), subject, body)