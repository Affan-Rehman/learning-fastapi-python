from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

roles_permissions = Table(
    "roles_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True, index=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True, index=True),
)


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
    permissions = relationship("Permission", secondary=roles_permissions, back_populates="roles")


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

