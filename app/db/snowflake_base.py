from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from snowflake.sqlalchemy import URL

class SnowflakeBase:
    def __init__(self):
        self.engine = create_async_engine(
            URL(
                account=settings.snowflake_account,
                user=settings.snowflake_user,
                password=settings.snowflake_password,
                database=settings.snowflake_database,
                schema=settings.snowflake_schema,
                warehouse=settings.snowflake_warehouse,
                role=settings.snowflake_role,
            ),
            echo=True,
            future=True,
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()