from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis
from app.security.config import SecurityConfig

# Redis client for session storage
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    def __init__(self):
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_until: Dict[str, datetime] = {}
    
    async def check_rate_limit(self, request: Request):
        """
        Verifica límites de tasa por IP
        """
        client_ip = request.client.host
        
        # Verificar límite por minuto
        minute_key = f"rate_limit:{client_ip}:minute"
        minute_count = redis_client.incr(minute_key)
        if minute_count == 1:
            redis_client.expire(minute_key, 60)
        
        if minute_count > SecurityConfig.RATE_LIMIT_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiadas solicitudes. Por favor, intente más tarde."
            )
        
        # Verificar límite por hora
        hour_key = f"rate_limit:{client_ip}:hour"
        hour_count = redis_client.incr(hour_key)
        if hour_count == 1:
            redis_client.expire(hour_key, 3600)
        
        if hour_count > SecurityConfig.RATE_LIMIT_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Se ha excedido el límite de solicitudes por hora."
            )
    
    def record_failed_attempt(self, username: str):
        """
        Registra un intento fallido de inicio de sesión
        """
        if username in self.failed_attempts:
            self.failed_attempts[username] += 1
        else:
            self.failed_attempts[username] = 1
            
        if self.failed_attempts[username] >= SecurityConfig.MAX_FAILED_LOGIN_ATTEMPTS:
            self.lockout_until[username] = datetime.now() + timedelta(
                minutes=SecurityConfig.LOCKOUT_DURATION_MINUTES
            )
    
    def check_lockout(self, username: str) -> bool:
        """
        Verifica si una cuenta está bloqueada
        """
        if username in self.lockout_until:
            if datetime.now() < self.lockout_until[username]:
                return True
            else:
                # Reset counters if lockout has expired
                del self.lockout_until[username]
                del self.failed_attempts[username]
        return False
    
    def reset_failed_attempts(self, username: str):
        """
        Resetea los contadores de intentos fallidos
        """
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.lockout_until:
            del self.lockout_until[username]
    
    async def manage_session(self, request: Request):
        """
        Gestiona la sesión del usuario
        """
        session_token = request.cookies.get("session_token")
        if session_token:
            session_data = redis_client.get(f"session:{session_token}")
            if session_data:
                # Renovar la sesión
                redis_client.expire(
                    f"session:{session_token}",
                    SecurityConfig.SESSION_EXPIRE_MINUTES * 60
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Sesión expirada"
                )

security_middleware = SecurityMiddleware()