from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database configuration
    database_url: str = f"sqlite:///{Path(__file__).parent.parent}/medcheck.db"
    
    # JWT configuration
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    token_url: str = "auth/jwt/login"
    
    # Snowflake configuration (for application data)
    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_database: str = "MEDCHECK"
    snowflake_schema: str = "PUBLIC"
    snowflake_warehouse: str = "COMPUTE_WH"
    snowflake_role: str = "ACCOUNTADMIN"

    class Config:
        env_file = ".env"

settings = Settings()