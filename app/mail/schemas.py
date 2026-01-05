from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """
    Base email schema for standard email sending.

    Attributes:
        email: List of recipient email addresses
        body: Optional body content (for template-based emails)
    """

    email: List[EmailStr]
    body: Dict[str, Any] | None = None


class EmailWithTemplateSchema(BaseModel):
    """
    Schema for template-based email sending.

    Attributes:
        email: List of recipient email addresses
        template_name: Name of the template file (without extension)
        body: Template variables as dictionary
    """

    email: List[EmailStr]
    template_name: str
    body: Dict[str, Any]


class EmailWithAttachmentSchema(BaseModel):
    """
    Schema for email with attachments.

    Attributes:
        email: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
    """

    email: List[EmailStr]
    subject: str
    body: str


class EmailMultipartSchema(BaseModel):
    """
    Schema for multipart email (HTML + plain text).

    Attributes:
        email: List of recipient email addresses
        subject: Email subject
        html_body: HTML content
        plain_text_body: Plain text content
    """

    email: List[EmailStr]
    subject: str
    html_body: str
    plain_text_body: str


class BulkEmailSchema(BaseModel):
    """
    Schema for bulk email sending.

    Attributes:
        emails: List of email schemas to send
    """

    emails: List[EmailSchema]

