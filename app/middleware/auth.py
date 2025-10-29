from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.security.config import SecurityConfig
from app.models.auth import TokenData
from app.services.auth_service import get_user
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError as e:
        logger.error(f"Error al decodificar token JWT: {str(e)}")
        raise credentials_exception
    
    user = await get_user(email=token_data.email)
    if user is None:
        logger.warning(f"Usuario no encontrado: {token_data.email}")
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user["active"]:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def check_admin_role(current_user = Depends(get_current_active_user)):
    if current_user["role"] != "admin":
        logger.warning(f"Intento de acceso a ruta de admin por usuario no autorizado: {current_user['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return current_user