from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.reminder import Reminder
from app.models.notification import WebPushSubscription
from app.services.push_service import PushService


class ReminderService:
    def __init__(self):
        self.push = PushService()

    def schedule_in_minutes(self, db: Session, user_id: int, title: str, body: str, minutes: int) -> Reminder:
        when = datetime.now(timezone.utc) + timedelta(minutes=max(0, minutes))
        rec = Reminder(user_id=user_id, title=title, body=body, scheduled_at=when)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    def list_upcoming(self, db: Session, user_id: int) -> List[Reminder]:
        now = datetime.now(timezone.utc)
        return (
            db.query(Reminder)
            .filter(Reminder.user_id == user_id, Reminder.active == True, Reminder.scheduled_at >= now)
            .order_by(Reminder.scheduled_at.asc())
            .limit(50)
            .all()
        )

    def process_due(self, db: Session) -> int:
        """Send all due reminders and mark them sent. Returns number sent."""
        now = datetime.now(timezone.utc)
        due: List[Reminder] = (
            db.query(Reminder)
            .filter(Reminder.active == True, Reminder.sent_at.is_(None), Reminder.scheduled_at <= now)
            .all()
        )
        count = 0
        for r in due:
            subs = db.query(WebPushSubscription).filter(WebPushSubscription.user_id == r.user_id).all()
            if not subs:
                # No subs, desactivar para no reintentar infinito
                r.active = False
                r.sent_at = now
                db.add(r)
                continue
            errors = []
            for s in subs:
                err = self.push.send(
                    s,
                    {
                        "title": r.title or "Recordatorio",
                        "body": r.body or "Tienes un recordatorio programado",
                        "url": "/reports/dashboard",
                    },
                )
                if err:
                    errors.append(err)
            r.sent_at = now
            r.active = False
            db.add(r)
            db.commit()
            count += 1
        return count
