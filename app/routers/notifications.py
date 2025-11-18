from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.auth.users import get_current_active_user
from app.models.user import User
from app.models.notification import WebPushSubscription
from app.services.push_service import PushService


router = APIRouter(prefix="/notifications", tags=["notifications"])
push = PushService()


@router.get("/public-key")
async def get_public_key():
    return {"publicKey": push.get_public_key()}


@router.post("/subscribe")
async def subscribe(
    sub: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        rec = push.save_subscription(db, current_user.id, sub)
        return {"status": "ok", "id": rec.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/test")
async def send_test(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    subs = db.query(WebPushSubscription).filter(WebPushSubscription.user_id == current_user.id).all()
    if not subs:
        raise HTTPException(status_code=404, detail="Sin suscripciones para el usuario")

    errors = []
    for s in subs:
        err = push.send(
            s,
            {
                "title": "MedCheck",
                "body": "🔔 Notificación de prueba: Recordatorios activos",
                "url": "/reports/dashboard",
            },
        )
        if err:
            errors.append({"id": s.id, "error": err})

    return {"sent": len(subs) - len(errors), "errors": errors}


@router.get("/subscriptions")
async def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    subs = db.query(WebPushSubscription).filter(WebPushSubscription.user_id == current_user.id).all()
    return {
        "count": len(subs),
        "items": [
            {"id": s.id, "endpoint": s.endpoint[-25:], "created_at": s.created_at.isoformat() if s.created_at else None}
            for s in subs
        ],
    }
