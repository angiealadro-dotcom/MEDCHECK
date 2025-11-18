from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.alert_service import AlertService
from app.db.database import SessionLocal
from app.services.reminder_service import ReminderService

def setup_scheduler(app: FastAPI):
    scheduler = AsyncIOScheduler()
    alert_service = AlertService()
    reminder_service = ReminderService()

    # Programar procesamiento de alertas cada hora
    scheduler.add_job(
        alert_service.process_alerts,
        'interval',
        hours=1,
        id='process_alerts'
    )

    # Procesar recordatorios cada minuto
    def _process_reminders_job():
        db = SessionLocal()
        try:
            sent = reminder_service.process_due(db)
            if sent:
                print(f"[scheduler] Recordatorios enviados: {sent}")
        finally:
            db.close()

    scheduler.add_job(
        _process_reminders_job,
        'interval',
        minutes=1,
        id='process_reminders'
    )

    scheduler.start()
    app.state.scheduler = scheduler  # Guardar referencia al scheduler
