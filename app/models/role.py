from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Role(Base):
    """
    Role model for RBAC system.

    Attributes:
        id: Primary key
        name: Role name (unique, indexed)
        description: Role description
        created_at: Timestamp when role was created
        updated_at: Timestamp when role was last updated
        users: Relationship to users with this role
        permissions: Many-to-many relationship with permissions
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="roles_permissions", back_populates="roles")
