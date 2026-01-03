from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

roles_permissions = Table(
    "roles_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True, index=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True, index=True),
)


class Permission(Base):
    """
    Permission model for RBAC system.

    Attributes:
        id: Primary key
        name: Permission name (unique, indexed)
        description: Permission description
        created_at: Timestamp when permission was created
        updated_at: Timestamp when permission was last updated
        roles: Many-to-many relationship with roles
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    roles = relationship("Role", secondary=roles_permissions, back_populates="permissions")

