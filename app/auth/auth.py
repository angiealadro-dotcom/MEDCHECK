from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.database import User

# Configuración de JWT
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    default="bcrypt",
    deprecated="auto",
    bcrypt__truncate_error=False,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    is_pbkdf2 = isinstance(hashed_password, str) and hashed_password.startswith("$pbkdf2-sha256$")
    if isinstance(plain_password, str) and not is_pbkdf2:
        b = plain_password.encode('utf-8')[:72]
        try:
            plain_password = b.decode('utf-8')
        except UnicodeDecodeError:
            plain_password = b.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    if isinstance(password, str):
        b = password.encode('utf-8')
        orig_len = len(b)
        b = b[:72]
        try:
            password = b.decode('utf-8')
        except UnicodeDecodeError:
            password = b.decode('utf-8', errors='ignore')
    # Si la contraseña original excedía 72 bytes, usar PBKDF2-SHA256 para evitar límite bcrypt
    try:
        if orig_len > 72:
            return pbkdf2_sha256.hash(password)
        return pwd_context.hash(password)
    except Exception:
        return pbkdf2_sha256.hash(password)

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user