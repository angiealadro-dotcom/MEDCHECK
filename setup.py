import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker, create_db_and_tables
from app.models.user import User
from app.auth.users import UserManager, get_user_db

async def init_db():
    await create_db_and_tables()
    print("Database tables created successfully")

async def create_admin():
    async with async_session_maker() as session:
        user_db = await anext(get_user_db(session))
        user_manager = UserManager(user_db)
        
        try:
            user = await user_manager.create(
                {
                    "email": "admin@medcheck.com",
                    "password": "admin123",  # Change this in production
                    "is_superuser": True,
                    "is_verified": True,
                }
            )
            print(f"Admin user created successfully with ID: {user.id}")
        except Exception as e:
            print(f"Error creating admin user: {e}")

async def main():
    await init_db()
    await create_admin()

if __name__ == "__main__":
    asyncio.run(main())