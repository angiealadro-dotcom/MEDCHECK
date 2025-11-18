from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Admin dentro de su organización
    is_super_admin = Column(Boolean, default=False)  # Super admin de toda la plataforma

    # Multi-tenancy: cada usuario pertenece a una organización
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    # organization = relationship("Organization", back_populates="users")
