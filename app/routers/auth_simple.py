from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.auth.users import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    get_user_by_username,
    get_user_by_email
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool
    
    class Config:
        from_attributes = True

@router.post("/login", response_model=Token)
async def login(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    try:
        print(f"[LOGIN] Intentando autenticar usuario: {form_data.username}")
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            print(f"[LOGIN] Fallo de autenticación para: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"[LOGIN] Usuario autenticado exitosamente: {user.username}")
        access_token = create_access_token(data={"sub": user.username})
        
        # Guardar el token en una cookie HTTP-only
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # No accesible desde JavaScript (más seguro)
            max_age=86400,  # 24 horas en segundos
            samesite="lax"  # Protección CSRF
        )
        
        print(f"[LOGIN] Token creado y cookie configurada para: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN ERROR] Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear nuevo usuario
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/logout")
async def logout(response: Response):
    """
    Cerrar sesión eliminando la cookie del token
    """
    response.delete_cookie(key="access_token")
    return {"message": "Sesión cerrada exitosamente"}
