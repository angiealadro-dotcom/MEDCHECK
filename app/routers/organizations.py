"""
Router para gestión de organizaciones y registro multi-tenant
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import re

from app.db.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.organization_schemas import OrganizationCreate, OrganizationResponse, OrganizationStats
from app.auth.users import get_password_hash, get_current_user

router = APIRouter(prefix="/organizations", tags=["organizations"])
templates = Jinja2Templates(directory="templates")

def generate_slug(name: str) -> str:
    """Genera un slug único a partir del nombre"""
    # Convertir a minúsculas y reemplazar espacios
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remover caracteres especiales
    slug = re.sub(r'[-\s]+', '-', slug)  # Reemplazar espacios con guiones
    return slug[:100]  # Limitar longitud

@router.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    """Mostrar formulario de registro de organización"""
    return templates.TemplateResponse("organization_register.html", {
        "request": request,
        "title": "Registrar Organización"
    })

@router.post("/register", response_model=OrganizationResponse)
async def register_organization(org_data: OrganizationCreate, db: Session = Depends(get_db)):
    """
    Registrar una nueva organización con su administrador
    """
    # Verificar que no exista el email
    existing_user = db.query(User).filter(User.email == org_data.admin_email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con ese email"
        )
    
    # Generar slug único
    base_slug = generate_slug(org_data.name)
    slug = base_slug
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Crear organización
    trial_end = datetime.utcnow() + timedelta(days=30)  # 30 días de trial
    new_org = Organization(
        name=org_data.name,
        slug=slug,
        contact_email=org_data.contact_email,
        contact_phone=org_data.contact_phone,
        institution_type=org_data.institution_type,
        country=org_data.country,
        city=org_data.city,
        address=org_data.address,
        is_active=True,
        plan="free",
        max_users=5,
        trial_ends_at=trial_end
    )
    
    db.add(new_org)
    db.flush()  # Para obtener el ID
    
    # Crear usuario administrador
    hashed_password = get_password_hash(org_data.admin_password)
    admin_user = User(
        email=org_data.admin_email,
        username=org_data.admin_email.split('@')[0],  # Usar parte antes del @
        hashed_password=hashed_password,
        full_name=org_data.admin_name,
        is_active=True,
        is_admin=True,
        is_super_admin=False,
        organization_id=new_org.id
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(new_org)
    
    return new_org

@router.get("/list", response_class=HTMLResponse)
async def list_organizations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Panel de administración de organizaciones (solo super admin)"""
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Obtener todas las organizaciones con estadísticas
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    
    org_stats = []
    for org in orgs:
        # Contar usuarios
        total_users = db.query(func.count(User.id)).filter(
            User.organization_id == org.id
        ).scalar() or 0
        
        active_users = db.query(func.count(User.id)).filter(
            User.organization_id == org.id,
            User.is_active == True
        ).scalar() or 0
        
        # Contar checklists (importar modelo si existe)
        try:
            from app.models.checklist_entry import ChecklistEntrySQL
            total_checklists = db.query(func.count(ChecklistEntrySQL.id)).filter(
                ChecklistEntrySQL.organization_id == org.id
            ).scalar() or 0
        except:
            total_checklists = 0
        
        org_stats.append({
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "contact_email": org.contact_email,
            "institution_type": org.institution_type,
            "country": org.country,
            "city": org.city,
            "plan": org.plan,
            "is_active": org.is_active,
            "created_at": org.created_at,
            "trial_ends_at": org.trial_ends_at,
            "total_users": total_users,
            "active_users": active_users,
            "total_checklists": total_checklists
        })
    
    return templates.TemplateResponse("super_admin_dashboard.html", {
        "request": request,
        "title": "Panel de Super Admin",
        "organizations": org_stats,
        "current_user": current_user
    })

@router.post("/{org_id}/toggle-active")
async def toggle_organization_active(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activar/desactivar una organización"""
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    
    org.is_active = not org.is_active
    db.commit()
    
    return {"success": True, "is_active": org.is_active}

@router.get("/api/stats")
async def get_platform_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Estadísticas generales de la plataforma"""
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    total_orgs = db.query(func.count(Organization.id)).scalar() or 0
    active_orgs = db.query(func.count(Organization.id)).filter(Organization.is_active == True).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    return {
        "total_organizations": total_orgs,
        "active_organizations": active_orgs,
        "total_users": total_users,
        "timestamp": datetime.utcnow()
    }
