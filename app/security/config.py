from datetime import timedelta
from pydantic import BaseModel, Field
import re
from typing import List

class SecurityConfig:
    # JWT Settings
    JWT_SECRET_KEY = "93c1e171c7e6f9381f6b6950c92c3bb672104b4dcf5c37ea8e8066c86d3f98e5"  # Should be in .env
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

    # Password Policy
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 50
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    PASSWORD_MAX_REPEATED_CHARS = 3

    # Session Management
    SESSION_EXPIRE_MINUTES = 30
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Rate Limiting
    RATE_LIMIT_MINUTE = 30  # requests per minute
    RATE_LIMIT_HOUR = 1000   # requests per hour
    
    # Access Control
    PROTECTED_ROUTES = [
        "/checklist/.*",
        "/reports/.*",
        "/users/.*"
    ]
    
    # Roles and Permissions
    ROLE_PERMISSIONS = {
        "admin": ["all"],
        "supervisor": [
            "view_reports",
            "manage_checklists",
            "view_users",
            "manage_area"
        ],
        "enfermero": [
            "create_checklist",
            "view_own_checklists",
            "view_own_area"
        ]
    }

    @classmethod
    def validate_password(cls, password: str) -> List[str]:
        """
        Valida que la contraseña cumpla con los requisitos de seguridad
        Retorna lista de errores, vacía si la contraseña es válida
        """
        errors = []
        
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            errors.append(f"La contraseña debe tener al menos {cls.PASSWORD_MIN_LENGTH} caracteres")
            
        if len(password) > cls.PASSWORD_MAX_LENGTH:
            errors.append(f"La contraseña no puede tener más de {cls.PASSWORD_MAX_LENGTH} caracteres")
            
        if cls.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
            
        if cls.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
            
        if cls.PASSWORD_REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("La contraseña debe contener al menos un número")
            
        if cls.PASSWORD_REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.PASSWORD_SPECIAL_CHARS)}]', password):
            errors.append("La contraseña debe contener al menos un carácter especial")
            
        # Verificar caracteres repetidos
        for i in range(len(password) - cls.PASSWORD_MAX_REPEATED_CHARS + 1):
            if len(set(password[i:i + cls.PASSWORD_MAX_REPEATED_CHARS])) == 1:
                errors.append(f"La contraseña no puede tener más de {cls.PASSWORD_MAX_REPEATED_CHARS} caracteres iguales seguidos")
                break
                
        return errors

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """
        Verifica si un rol tiene un permiso específico
        """
        if role not in cls.ROLE_PERMISSIONS:
            return False
            
        permissions = cls.ROLE_PERMISSIONS[role]
        return "all" in permissions or permission in permissions