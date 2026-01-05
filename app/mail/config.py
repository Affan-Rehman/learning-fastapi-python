from pathlib import Path

from fastapi_mail import ConnectionConfig

from app.core.config import settings


def get_mail_config() -> ConnectionConfig:
    """
    Get FastMail connection configuration from settings.

    Returns:
        ConnectionConfig instance with mail settings
    """
    # Only create config if mail settings are provided
    if not settings.MAIL_FROM or not settings.MAIL_SERVER:
        # Return a minimal config that won't be used until properly configured
        return ConnectionConfig(
            MAIL_USERNAME="",
            MAIL_PASSWORD="",
            MAIL_FROM="noreply@example.com",
            MAIL_PORT=587,
            MAIL_SERVER="localhost",
            MAIL_FROM_NAME="",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=False,
            VALIDATE_CERTS=True,
        )

    template_folder = Path(__file__).parent / "templates"
    
    config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
        TEMPLATE_FOLDER=template_folder if template_folder.exists() else (Path(settings.MAIL_TEMPLATE_FOLDER) if settings.MAIL_TEMPLATE_FOLDER else None),
    )

    return config


mail_config = get_mail_config()

