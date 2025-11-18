from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.users import get_current_active_user
from app.models.user import User
from app.services.reminder_service import ReminderService


router = APIRouter(prefix="/reminders", tags=["reminders"])
service = ReminderService()


class QuickReminderIn(BaseModel):
    minutes: int = Field(ge=0, le=7 * 24 * 60, description="Minutos a partir de ahora")
    title: Optional[str] = Field(default="Recordatorio MedCheck")
    body: Optional[str] = Field(default="Tienes un recordatorio pendiente")


@router.get("")
async def list_my_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    items = service.list_upcoming(db, current_user.id)
    return {
        "count": len(items),
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None,
                "active": r.active,
            }
            for r in items
        ],
    }


@router.post("/quick")
async def schedule_quick(
    payload: QuickReminderIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rec = service.schedule_in_minutes(db, current_user.id, payload.title or "Recordatorio MedCheck", payload.body or "", payload.minutes)
    return {
        "status": "scheduled",
        "id": rec.id,
        "scheduled_at": rec.scheduled_at.isoformat() if rec.scheduled_at else None,
    }


@router.post("/send-now")
async def send_now(
    title: str = "MedCheck",
    body: str = "🔔 Recordatorio inmediato",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Programar en pasado y procesar inmediatamente
    service.schedule_in_minutes(db, current_user.id, title, body, 0)
    sent = service.process_due(db)
    if sent == 0:
        raise HTTPException(status_code=400, detail="No se pudo enviar (¿sin suscripciones?)")
    return {"sent": sent}
