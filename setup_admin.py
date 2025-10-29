import asyncio
from app.services.auth_service import create_user
from app.models.auth import UserCreate
from app.db.snowflake_db import init_snowflake
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_admin():
    # Inicializar la base de datos primero
    if not init_snowflake():
        logger.error("Error inicializando la base de datos Snowflake")
        return
    
    try:
        admin_user = UserCreate(
            username="admin",
            email="admin@medcheck.com",
            password="MedCheck2023!",  # Cambiar esta contraseña en producción
            role="admin",
            full_name="Administrador del Sistema"
        )
        
        user = await create_user(admin_user)
        logger.info(f"Usuario administrador creado exitosamente: {user['email']}")
        
    except Exception as e:
        logger.error(f"Error al crear usuario administrador: {str(e)}")

if __name__ == "__main__":
    asyncio.run(setup_admin())