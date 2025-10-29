from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.db.snowflake_db import get_snowflake_cursor
from app.models.auth import UserCreate, User, TokenData
from app.security.config import SecurityConfig

import os
import uuid
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, stored_password: str) -> bool:
    # Separar el salt y el hash almacenados
    salt_str, hash_str = stored_password.split(':')
    salt = bytes.fromhex(salt_str)
    stored_hash = bytes.fromhex(hash_str)
    
    # Calcular el hash de la contraseña proporcionada
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256', 
        plain_password.encode('utf-8'), 
        salt, 
        100000
    )
    
    # Comparar los hashes
    return hash_obj == stored_hash

def get_password_hash(password: str) -> str:
    salt = os.urandom(32)
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt.hex() + ':' + hash_obj.hex()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(days=SecurityConfig.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = jwt.encode(
        {"sub": username, "exp": expire},
        SecurityConfig.JWT_SECRET_KEY,
        algorithm=SecurityConfig.JWT_ALGORITHM
    )
    return refresh_token

async def create_user(user: UserCreate):
    from app.db.snowflake_db import get_snowflake_cursor
    cursor = next(get_snowflake_cursor())
    try:
        hashed_password = get_password_hash(user.password)
        cursor.execute("""
            insert into users (username, email, full_name, area, password_hash, role)
            values (%s, %s, %s, %s, %s, %s)
        """, (
            user.username,
            user.email,
            user.full_name,
            user.area,
            hashed_password,
            user.role
        ))
        cursor.connection.commit()
        
        # Consultar el usuario recién creado
        cursor.execute("""
            select id, username, email, role, active
            from users
            where username = %s
        """, (user.username,))
        new_user = cursor.fetchone()
        
        if new_user:
            return {
                "id": new_user[0],
                "username": new_user[1],
                "email": new_user[2],
                "role": new_user[3],
                "active": new_user[4]
            }
    except Exception as e:
        if cursor and cursor.connection:
            cursor.connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()

def create_session_token() -> str:
    return str(uuid.uuid4())

async def get_user(email: str) -> Optional[dict]:
    cursor = next(get_snowflake_cursor())
    try:
        cursor.execute("""
            SELECT * FROM users 
            WHERE email = %s AND activo = TRUE
        """, (email,))
        user = cursor.fetchone()
        if user:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, user))
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
    return None

async def authenticate_user(username: str, password: str) -> Tuple[Optional[dict], Optional[str]]:
    # Verificar bloqueo de cuenta
    if security_middleware.check_lockout(username):
        return None, "Cuenta temporalmente bloqueada por múltiples intentos fallidos"

    user = await get_user(username)
    if not user:
        security_middleware.record_failed_attempt(username)
        return None, "Usuario o contraseña incorrectos"

    if not verify_password(password, user["HASHED_PASSWORD"]):
        security_middleware.record_failed_attempt(username)
        return None, "Usuario o contraseña incorrectos"

    # Éxito - resetear intentos fallidos
    security_middleware.reset_failed_attempts(username)
    return user, None

async def create_user(user: UserCreate) -> Optional[dict]:
    # Validar política de contraseña
    password_errors = SecurityConfig.validate_password(user.password)
    if password_errors:
        raise ValueError(", ".join(password_errors))

    cursor = next(get_snowflake_cursor())
    try:
        # Verificar si el usuario ya existe
        cursor.execute(
            "SELECT 1 FROM users WHERE username = %s OR email = %s",
            (user.username, user.email)
        )
        if cursor.fetchone():
            raise ValueError("El usuario o email ya existe")

        hashed_password = get_password_hash(user.password)
        cursor.execute("""
            INSERT INTO users (
                username, email, hashed_password, full_name, 
                role, area, is_active, last_password_change
            )
            VALUES (%s, %s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP())
            RETURNING *
        """, (
            user.username,
            user.email,
            hashed_password,
            user.full_name,
            user.role,
            user.area
        ))
        cursor.connection.commit()
        
        new_user = cursor.fetchone()
        if new_user:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, new_user))
            
    except Exception as e:
        print(f"Error creando usuario: {e}")
        cursor.connection.rollback()
        raise e

async def update_last_login(username: str):
    """Actualiza la fecha del último inicio de sesión"""
    cursor = next(get_snowflake_cursor())
    try:
        cursor.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP()
            WHERE username = %s
        """, (username,))
        cursor.connection.commit()
    except Exception as e:
        print(f"Error actualizando último login: {e}")
        cursor.connection.rollback()

async def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Cambia la contraseña del usuario"""
    user = await get_user(username)
    if not user:
        return False, "Usuario no encontrado"

    if not verify_password(old_password, user["HASHED_PASSWORD"]):
        return False, "Contraseña actual incorrecta"

    # Validar nueva contraseña
    password_errors = SecurityConfig.validate_password(new_password)
    if password_errors:
        return False, ", ".join(password_errors)

    cursor = next(get_snowflake_cursor())
    try:
        hashed_password = get_password_hash(new_password)
        cursor.execute("""
            UPDATE users 
            SET hashed_password = %s, 
                last_password_change = CURRENT_TIMESTAMP()
            WHERE username = %s
        """, (hashed_password, username))
        cursor.connection.commit()
        return True, "Contraseña actualizada exitosamente"
    except Exception as e:
        cursor.connection.rollback()
        return False, f"Error actualizando contraseña: {str(e)}"