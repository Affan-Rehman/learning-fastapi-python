from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.users.models import User


class PermissionChecker:
    """
    Dependency class for checking user permissions.

    Usage:
        Depends(PermissionChecker("read_user"))
        Depends(PermissionChecker(["read_user", "update_user"]))
    """

    def __init__(self, required_permissions: str | list[str]):
        """
        Initialize permission checker.

        Args:
            required_permissions: Single permission name or list of permission names
        """
        if isinstance(required_permissions, str):
            self.required_permissions = [required_permissions]
        else:
            self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        Check if current user has required permissions.

        Args:
            current_user: Current authenticated user (from get_current_user dependency)

        Returns:
            Current user if permissions check passes

        Raises:
            HTTPException: 403 if user doesn't have required permissions
        """
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned",
            )

        user_permissions = {perm.name for perm in current_user.role.permissions}

        for required_perm in self.required_permissions:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{required_perm}' required",
                )

        return current_user


class RoleChecker:
    """
    Dependency class for checking user roles.

    Usage:
        Depends(RoleChecker(["admin", "moderator"]))
    """

    def __init__(self, allowed_roles: list[str]):
        """
        Initialize role checker.

        Args:
            allowed_roles: List of allowed role names
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        Check if current user has one of the allowed roles.

        Args:
            current_user: Current authenticated user (from get_current_user dependency)

        Returns:
            Current user if role check passes

        Raises:
            HTTPException: 403 if user doesn't have allowed role
        """
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned",
            )

        if current_user.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.name}' not allowed. Required: {self.allowed_roles}",
            )

        return current_user
