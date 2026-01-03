"""Seed RBAC data

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:01:00.000000

"""
from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    roles_permissions_table = sa.table(
        "roles_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
    )

    now = datetime.utcnow()

    op.bulk_insert(
        roles_table,
        [
            {
                "id": 1,
                "name": "admin",
                "description": "Administrator with all permissions",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 2,
                "name": "user",
                "description": "Regular user",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 3,
                "name": "moderator",
                "description": "Moderator with limited admin permissions",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    op.bulk_insert(
        permissions_table,
        [
            {
                "id": 1,
                "name": "create_user",
                "description": "Create new users",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 2,
                "name": "read_user",
                "description": "Read user information",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 3,
                "name": "update_user",
                "description": "Update user information",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 4,
                "name": "delete_user",
                "description": "Delete users",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 5,
                "name": "manage_roles",
                "description": "Manage roles and permissions",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    op.bulk_insert(
        roles_permissions_table,
        [
            {"role_id": 1, "permission_id": 1},
            {"role_id": 1, "permission_id": 2},
            {"role_id": 1, "permission_id": 3},
            {"role_id": 1, "permission_id": 4},
            {"role_id": 1, "permission_id": 5},
            {"role_id": 2, "permission_id": 2},
            {"role_id": 3, "permission_id": 2},
            {"role_id": 3, "permission_id": 3},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM roles_permissions")
    op.execute("DELETE FROM permissions")
    op.execute("DELETE FROM roles")
