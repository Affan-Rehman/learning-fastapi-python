from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    API_V1_PREFIX: str
    HOST: str
    PORT: int = 8000
    ENVIRONMENT: str

    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int
    FRONTEND_URL: str

    CORS_ORIGINS: str

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTHENTICATED: int = 100
    RATE_LIMIT_UNAUTHENTICATED: int = 20
    RATE_LIMIT_AUTH_ENDPOINTS: int = 5

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"

    CREATE_DEFAULT_ADMIN: bool = Field(default=False)
    DEFAULT_ADMIN_EMAIL: str = Field(default="")
    DEFAULT_ADMIN_USERNAME: str = Field(default="")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="")

    # Mail settings
    MAIL_USERNAME: str = Field(default="")
    MAIL_PASSWORD: str = Field(default="")
    MAIL_FROM: str = Field(default="")
    MAIL_PORT: int = Field(default=587)
    MAIL_SERVER: str = Field(default="")
    MAIL_FROM_NAME: str = Field(default="")
    MAIL_STARTTLS: bool = Field(default=True)
    MAIL_SSL_TLS: bool = Field(default=False)
    MAIL_USE_CREDENTIALS: bool = Field(default=True)
    MAIL_VALIDATE_CERTS: bool = Field(default=True)
    MAIL_TEMPLATE_FOLDER: str | None = Field(default=None)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
