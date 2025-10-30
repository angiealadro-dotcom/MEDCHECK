from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.schemas import ChecklistForm
from app.models.checklist_entry import ChecklistEntrySQL


def create_entries_from_form(db: Session, form: ChecklistForm, username: str | None = None) -> List[ChecklistEntrySQL]:
    created: List[ChecklistEntrySQL] = []
    observaciones = form.observaciones or None

    # Esperamos estructura: items: { prescripcion: {...}, preparacion: {...}, administracion: {...} }
    for etapa, items in (form.items or {}).items():
        for item_key, cumple in (items or {}).items():
            entry = ChecklistEntrySQL(
                area=form.area,
                turno=form.turno,
                protocolo_etapa=str(etapa),
                item=str(item_key),
                cumple=bool(cumple),
                observaciones=observaciones,
                usuario=username or "demo",
                metadatos=None,
                fecha_hora=datetime.utcnow(),
            )
            db.add(entry)
            created.append(entry)

    db.commit()
    for e in created:
        db.refresh(e)
    return created


def get_recent_entries(db: Session, limit: int = 100) -> List[ChecklistEntrySQL]:
    return (
        db.query(ChecklistEntrySQL)
        .order_by(ChecklistEntrySQL.fecha_hora.desc())
        .limit(limit)
        .all()
    )
