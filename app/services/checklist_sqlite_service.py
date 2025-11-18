from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.schemas import ChecklistForm
from app.models.checklist_entry import ChecklistEntrySQL


def create_entries_from_form(db: Session, form: ChecklistForm, username: str | None = None) -> List[ChecklistEntrySQL]:
    created: List[ChecklistEntrySQL] = []
    observaciones = form.observaciones or None

    # Extraer los 10 Correctos de administración
    admin_items = (form.items or {}).get('administracion', {})
    diez_correctos = {
        'paciente_correcto': admin_items.get('paciente_correcto', False),
        'medicamento_correcto': admin_items.get('medicamento_correcto', False),
        'dosis_correcta': admin_items.get('dosis_correcta', False),
        'via_correcta': admin_items.get('via_correcta', False),
        'hora_correcta': admin_items.get('hora_correcta', False),
        'fecha_vencimiento_verificada': admin_items.get('fecha_vencimiento_verificada', False),
        'educacion_paciente': admin_items.get('educacion_paciente', False),
        'registro_correcto': admin_items.get('registro_correcto', False),
        'alergias_verificadas': admin_items.get('alergias_verificadas', False),
        'responsabilidad_personal': admin_items.get('responsabilidad_personal', False),
    }

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
                # Agregar los 10 Correctos a TODAS las entradas (para administración tendrán valores reales)
                **diez_correctos
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
