from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path
import logging

class Settings(BaseSettings):
    model_config = ConfigDict(extra='allow', env_file='.env', env_file_encoding='utf-8')

    # App configuration
    app_name: str = "MedCheck"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8002
    workers: int = 1

    # Database configuration
    database_url: str = f"sqlite:///{Path(__file__).parent.parent}/medcheck.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600

    # JWT configuration
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    token_url: str = "auth/jwt/login"
    access_token_expire_minutes: int = 30

    # CORS configuration
    cors_origins: list = ["http://localhost:8002", "http://127.0.0.1:8002"]

    # ElevenLabs API (Text-to-Speech)
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    # Snowflake configuration (for application data)
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_database: str = "MEDCHECK"
    snowflake_schema: str = "PUBLIC"
    snowflake_warehouse: str = "COMPUTE_WH"
    snowflake_role: str = "ACCOUNTADMIN"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    def configure_logging(self):
        """Configure application logging"""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

settings = Settings()
settings.configure_logging()
