from pydantic import BaseModel


class Token(BaseModel):
    """
    JWT token response schema.

    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
    """

    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    """
    User login request schema.

    Attributes:
        username: Username or email
        password: User password
    """

    username: str
    password: str


class UserRegister(BaseModel):
    """
    User registration request schema.

    Attributes:
        email: User email address
        username: Username
        password: User password
    """

    email: str
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    """
    Forgot password request schema.

    Attributes:
        email: User email address to send password reset link
    """

    email: str


class ResetPasswordRequest(BaseModel):
    """
    Reset password request schema.

    Attributes:
        token: Password reset token received via email
        new_password: New password to set
    """

    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """
    Change password request schema.

    Attributes:
        old_password: Current password for verification
        new_password: New password to set
    """

    old_password: str
    new_password: str


class PasswordResetResponse(BaseModel):
    """
    Password reset response schema.

    Attributes:
        message: Success message
    """

    message: str

