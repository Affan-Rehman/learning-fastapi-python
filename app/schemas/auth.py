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
