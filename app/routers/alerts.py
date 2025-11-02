from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.services.alert_service import AlertService
from app.auth.users import get_current_active_user
from app.models.user import User
from app.db.database import get_db
from sqlalchemy.orm import Session

# Import the AlertConfig model from models.alerts
from app.models.alerts import AlertConfig
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

templates = Jinja2Templates(directory="templates")

router = APIRouter()
alert_service = AlertService()

@router.get("/critical")
async def get_critical_alerts(
    current_user: User = Depends(get_current_user),
    area: Optional[str] = None
):
    """
    Obtener alertas críticas actuales
    """
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver alertas críticas"
        )
        
    # Si no es admin, solo puede ver alertas de su área
    if current_user.role != "admin":
        area = current_user.area
        
    alerts = await alert_service.get_critical_alerts(area)
    return alerts

@router.post("/process")
async def process_alerts(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Procesar y enviar alertas manualmente
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden procesar alertas manualmente"
        )
        
    background_tasks.add_task(alert_service.process_alerts)
    return {"message": "Procesamiento de alertas iniciado"}

@router.post("/test")
async def test_alert(
    email: str,
    current_user: User = Depends(get_current_user)
):
    """
    Enviar alerta de prueba
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden enviar alertas de prueba"
        )
        
    subject = "🔔 Alerta de Prueba - MedCheck"
    body = """
    <h2>Esta es una alerta de prueba</h2>
    <p>Si estás recibiendo este email, el sistema de alertas está configurado correctamente.</p>
    """
    
    success = await alert_service.send_email_alert(email, subject, body)
    if success:
        return {"message": "Alerta de prueba enviada correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar la alerta de prueba"
        )

@router.get("/config", response_class=HTMLResponse)
async def get_alert_config_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Página de configuración de alertas
    """
    logging.info("Accediendo a la página de configuración de alertas")
    logging.info(f"Usuario actual: {current_user.email} (role: {current_user.role})")

    if current_user.role != "admin":
        logging.warning(f"Intento de acceso no autorizado por {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a la configuración"
        )
        
    # Obtener lista de áreas
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT area FROM checklist_entries ORDER BY area")
        areas = [row[0] for row in cursor.fetchall()]
        
        # Para depuración
        print("Áreas encontradas:", areas)
        
        return templates.TemplateResponse(
            "alert_config.html",
            {
                "request": request,
                "current_user": current_user,
                "areas": areas
            }
        )
    finally:
        cursor.close()
        conn.close()
        
    # Obtener lista de áreas para el selector
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT area FROM checklist_entries ORDER BY area")
        areas = [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()
        
    return templates.TemplateResponse(
        "alert_config.html",
        {
            "request": request,
            "current_user": current_user,
            "areas": areas
        }
    )

@router.get("/configs")
async def get_alert_configs(
    current_user: User = Depends(get_current_user)
) -> List[AlertConfig]:
    """
    Obtener todas las configuraciones de alertas
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver configuraciones"
        )
    
    print("Obteniendo configuraciones de alertas...")
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = CURRENT_SCHEMA()
            AND table_name = 'ALERT_CONFIGS'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("La tabla ALERT_CONFIGS no existe, creándola...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_configs (
                id NUMBER AUTOINCREMENT,
                area STRING,
                umbral_critico FLOAT DEFAULT 70.0,
                umbral_advertencia FLOAT DEFAULT 85.0,
                emails_adicionales ARRAY,
                notificar_supervisores BOOLEAN DEFAULT TRUE,
                intervalo_horas INTEGER DEFAULT 24,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                PRIMARY KEY (id)
            )
            """)
            print("Tabla ALERT_CONFIGS creada exitosamente")
            
            # Insertar configuración por defecto
            cursor.execute("""
            INSERT INTO alert_configs (
                area, umbral_critico, umbral_advertencia, 
                emails_adicionales, notificar_supervisores, 
                intervalo_horas, activo
            ) VALUES (
                NULL, 70.0, 85.0, 
                ARRAY_CONSTRUCT(), TRUE, 
                24, TRUE
            )
            """)
            conn.commit()
            print("Configuración por defecto creada")
        
        print("Consultando configuraciones existentes...")
        cursor.execute("""
            SELECT * FROM alert_configs 
            ORDER BY created_at DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        configs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return configs
    finally:
        cursor.close()
        conn.close()

@router.get("/configs/{config_id}")
async def get_alert_config(
    config_id: int,
    current_user: User = Depends(get_current_user)
) -> AlertConfig:
    """
    Obtener una configuración específica
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver configuraciones"
        )
    
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM alert_configs WHERE id = %s", (config_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        return dict(zip(columns, row))
    finally:
        cursor.close()
        conn.close()

@router.post("/configs")
async def create_alert_config(
    config: AlertConfig,
    current_user: User = Depends(get_current_user)
) -> AlertConfig:
    """
    Crear una nueva configuración de alertas
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear configuraciones"
        )
    
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO alert_configs (
                area, umbral_critico, umbral_advertencia, 
                emails_adicionales, notificar_supervisores, 
                intervalo_horas, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            config.area,
            config.umbral_critico,
            config.umbral_advertencia,
            config.emails_adicionales,
            config.notificar_supervisores,
            config.intervalo_horas,
            config.activo
        ))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        conn.commit()
        return dict(zip(columns, row))
    finally:
        cursor.close()
        conn.close()
    
    # Obtener configuración actual
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT critical_threshold, check_frequency, additional_recipients, enabled
            FROM alert_config
            LIMIT 1
        """)
        config = cursor.fetchone()
        if not config:
            config = {
                "critical_threshold": 70,
                "check_frequency": 1,
                "additional_recipients": "",
                "enabled": True
            }
        else:
            config = {
                "critical_threshold": config[0],
                "check_frequency": config[1],
                "additional_recipients": config[2],
                "enabled": config[3]
            }
            
        # Obtener logs recientes
        cursor.execute("""
            SELECT fecha_hora, tipo, area, enviado
            FROM alert_logs
            ORDER BY fecha_hora DESC
            LIMIT 10
        """)
        alert_logs = cursor.fetchall()
            
    finally:
        cursor.close()
        
    return templates.TemplateResponse(
        "alert_config.html",
        {
            "request": request,
            "current_user": current_user,
            "config": config,
            "alert_logs": alert_logs
        }
    )

@router.post("/config")
async def update_alert_config(
    config: AlertConfig,
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar configuración de alertas
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden modificar la configuración"
        )
        
    conn = await get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            MERGE INTO alert_config t
            USING (SELECT 1) s
            ON (1=1)
            WHEN MATCHED THEN
                UPDATE SET
                    critical_threshold = %s,
                    check_frequency = %s,
                    additional_recipients = %s,
                    enabled = %s,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (critical_threshold, check_frequency, additional_recipients, enabled)
                VALUES (%s, %s, %s, %s)
        """, (
            config.critical_threshold,
            config.check_frequency,
            config.additional_recipients,
            config.enabled,
            config.critical_threshold,
            config.check_frequency,
            config.additional_recipients,
            config.enabled
        ))
        conn.commit()
        return {"message": "Configuración actualizada correctamente"}
    finally:
        cursor.close()