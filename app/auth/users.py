from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt as bcrypt_hash
from passlib.hash import pbkdf2_sha256
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.database import get_db
from app.config import settings

# Configurar bcrypt para no lanzar error con >72 bytes y truncar de forma segura
pwd_context = CryptContext(
    # Soportar bcrypt (por defecto) y fallback a PBKDF2-SHA256 sin límite de 72 bytes
    schemes=["bcrypt", "pbkdf2_sha256"],
    default="bcrypt",
    deprecated="auto",
    bcrypt__truncate_error=False,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Si el hash es PBKDF2-SHA256 no truncamos; si es bcrypt, truncamos a 72 bytes
    is_pbkdf2 = isinstance(hashed_password, str) and hashed_password.startswith("$pbkdf2-sha256$")
    if isinstance(plain_password, str) and not is_pbkdf2:
        b = plain_password.encode('utf-8')
        b = b[:72]
        try:
            plain_password = b.decode('utf-8')
        except UnicodeDecodeError:
            # Si cortamos un carácter multibyte, ignoramos los bytes finales
            plain_password = b.decode('utf-8', errors='ignore')
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"[VERIFY] is_pbkdf2={is_pbkdf2}, plain_len={len(plain_password)}, result={result}")
        return result
    except Exception as e:
        print(f"[VERIFY][ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def get_password_hash(password: str) -> str:
    # Bcrypt tiene un límite de 72 bytes - truncar de forma segura en bytes
    if isinstance(password, str):
        b = password.encode('utf-8')
        orig_len = len(b)
        b72 = b[:72]
        try:
            p72 = b72.decode('utf-8')
        except UnicodeDecodeError:
            p72 = b72.decode('utf-8', errors='ignore')
        # Debug suave para diagnosticar problemas puntuales de longitud
        try:
            print(f"[PWD_HASH] len_bytes_orig={orig_len} len_bytes_trunc={len(b72)} text_len={len(p72)}")
        except Exception:
            pass
    try:
        # Si la contraseña supera 72 bytes, usar PBKDF2-SHA256 para evitar límites de bcrypt
        if orig_len > 72:
            return pbkdf2_sha256.hash(password)
        # Caso normal: bcrypt
        return pwd_context.hash(p72)
    except Exception as e:
        # Fallback explícito si alguna configuración de backend lanza error por longitud
        try:
            print(f"[PWD_HASH][fallback] Using bcrypt_hash. Cause: {e}")
        except Exception:
            pass
        try:
            return bcrypt_hash.using(truncate_error=False).hash(p72)
        except Exception:
            # Fallback final a PBKDF2-SHA256
            return pbkdf2_sha256.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    try:
        print(f"[AUTH] lookup username={username!r} -> {'FOUND' if user else 'NONE'}")
        if not user:
            return False
        # Diagnóstico detallado para producción
        print(f"[AUTH] user.hashed_password[:20]={user.hashed_password[:20] if user.hashed_password else 'NONE'}")
        print(f"[AUTH] password length={len(password)}, first_char={password[0] if password else 'EMPTY'}")
        ok = verify_password(password, user.hashed_password)
        print(f"[AUTH] verify_password returned: {ok}")
        if not ok:
            return False
        return user
    except Exception as e:
        print(f"[AUTH][ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(default=None)
):
    """
    Obtiene el usuario actual desde el token JWT.
    Busca el token primero en cookies, luego en el header Authorization.
    """
    # Intentar obtener el token de la cookie primero, luego del header
    token_to_use = access_token or token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token_to_use:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token_to_use, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user