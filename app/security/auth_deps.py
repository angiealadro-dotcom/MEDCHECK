from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.security.config import SecurityConfig
from app.models.auth import TokenData, User as UserPydantic
from app.models.user import User as UserSQL
from app.db.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserPydantic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Buscar usuario en la base de datos
        user_sql = db.query(UserSQL).filter(UserSQL.email == email).first()
        if user_sql is None:
            raise credentials_exception
        
        # Convertir a Pydantic model
        user = UserPydantic.from_orm(user_sql)
        return user
        
    except JWTError as e:
        logger.error(f"Error al decodificar token JWT: {str(e)}")
        raise credentials_exception