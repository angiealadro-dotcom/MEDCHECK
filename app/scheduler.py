from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.alert_service import AlertService

def setup_scheduler(app: FastAPI):
    scheduler = AsyncIOScheduler()
    alert_service = AlertService()
    
    # Programar procesamiento de alertas cada hora
    scheduler.add_job(
        alert_service.process_alerts,
        'interval',
        hours=1,
        id='process_alerts'
    )
    
    scheduler.start()
    app.state.scheduler = scheduler  # Guardar referencia al scheduler