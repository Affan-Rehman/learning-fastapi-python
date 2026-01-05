from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    User model with RBAC support.

    Attributes:
        id: Primary key
        email: User email address (unique, indexed)
        username: Username (unique, indexed)
        hashed_password: Bcrypt hashed password
        role_id: Foreign key to roles table (indexed)
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
        role: Relationship to user's role
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    role = relationship("Role", back_populates="users")

