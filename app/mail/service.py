from typing import List

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType, MultipartSubtypeEnum

from app.mail.config import mail_config

# Initialize FastMail instance
fm = FastMail(mail_config)


async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html,
    attachments: List | None = None,
) -> bool:
    """
    Send a standard email.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
        subtype: Message type (html or plain), defaults to html
        attachments: Optional list of file attachments

    Returns:
        True if email was sent successfully

    Example:
        ```python
        from app.mail.service import send_email

        await send_email(
            recipients=["user@example.com"],
            subject="Welcome!",
            body="<h1>Welcome to our platform</h1>",
            subtype=MessageType.html
        )
        ```
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
        attachments=attachments or [],
    )
    await fm.send_message(message)
    return True


async def send_email_background(
    background_tasks: BackgroundTasks,
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html,
    attachments: List | None = None,
) -> bool:
    """
    Send email as a background task (non-blocking).

    Args:
        background_tasks: FastAPI BackgroundTasks instance
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
        subtype: Message type (html or plain), defaults to html
        attachments: Optional list of file attachments

    Returns:
        True immediately (email sent in background)

    Example:
        ```python
        from fastapi import BackgroundTasks
        from app.mail.service import send_email_background

        @app.post("/endpoint")
        async def my_endpoint(background_tasks: BackgroundTasks):
            await send_email_background(
                background_tasks=background_tasks,
                recipients=["user@example.com"],
                subject="Notification",
                body="Your request has been processed"
            )
            return {"message": "Email queued"}
        ```
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
        attachments=attachments or [],
    )
    background_tasks.add_task(fm.send_message, message)
    return True


async def send_email_with_template(
    recipients: List[str],
    subject: str,
    template_name: str,
    template_body: dict,
    html_template: str | None = None,
    plain_template: str | None = None,
) -> bool:
    """
    Send email using Jinja2 template.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        template_name: Template file name (if using single template)
        template_body: Dictionary of template variables
        html_template: HTML template file name (if using separate templates)
        plain_template: Plain text template file name (if using separate templates)

    Returns:
        True if email was sent successfully

    Example:
        ```python
        from app.mail.service import send_email_with_template

        await send_email_with_template(
            recipients=["user@example.com"],
            subject="Welcome!",
            template_name="welcome.html",
            template_body={"name": "John", "activation_link": "https://..."}
        )
        ```
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        subtype=MessageType.html,
    )

    if html_template and plain_template:
        await fm.send_message(message, html_template=html_template, plain_template=plain_template)
    else:
        await fm.send_message(message, template_name=template_name)

    return True


async def send_email_with_attachments(
    recipients: List[str],
    subject: str,
    body: str,
    attachments: List,
    subtype: MessageType = MessageType.html,
) -> bool:
    """
    Send email with file attachments.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
        attachments: List of attachment objects (can be UploadFile, file paths, or dicts with file info)
        subtype: Message type (html or plain), defaults to html

    Returns:
        True if email was sent successfully

    Example:
        ```python
        from app.mail.service import send_email_with_attachments

        # With file path
        await send_email_with_attachments(
            recipients=["user@example.com"],
            subject="Report",
            body="Please find the report attached",
            attachments=["/path/to/file.pdf"]
        )

        # With inline image (Content-ID)
        await send_email_with_attachments(
            recipients=["user@example.com"],
            subject="Newsletter",
            body='<img src="cid:logo_image@fastapi-mail">',
            attachments=[{
                "file": "/path/to/logo.png",
                "headers": {
                    "Content-ID": "<logo_image@fastapi-mail>",
                    "Content-Disposition": "inline; filename=\\"logo.png\\""
                },
                "mime_type": "image",
                "mime_subtype": "png"
            }]
        )
        ```
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
        attachments=attachments,
    )
    await fm.send_message(message)
    return True


async def send_multipart_email(
    recipients: List[str],
    subject: str,
    html_body: str,
    plain_text_body: str,
) -> bool:
    """
    Send multipart email with both HTML and plain text content.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        html_body: HTML email content
        plain_text_body: Plain text email content

    Returns:
        True if email was sent successfully

    Example:
        ```python
        from app.mail.service import send_multipart_email

        await send_multipart_email(
            recipients=["user@example.com"],
            subject="Newsletter",
            html_body="<h1>Welcome</h1><p>HTML content here</p>",
            plain_text_body="Welcome\n\nPlain text content here"
        )
        ```
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html_body,
        subtype=MessageType.html,
        alternative_body=plain_text_body,
        multipart_subtype=MultipartSubtypeEnum.alternative,
    )
    await fm.send_message(message)
    return True


async def send_bulk_emails(messages: List[MessageSchema]) -> bool:
    """
    Send multiple emails using a single SMTP connection.

    More efficient than sending emails individually as it reuses
    the SMTP connection for all messages.

    Args:
        messages: List of MessageSchema objects to send

    Returns:
        True if all emails were sent successfully

    Example:
        ```python
        from app.mail.service import send_bulk_emails
        from fastapi_mail import MessageSchema, MessageType

        messages = [
            MessageSchema(
                subject="Welcome!",
                recipients=["user1@example.com"],
                body="<p>Thanks for joining.</p>",
                subtype=MessageType.html,
            ),
            MessageSchema(
                subject="Verify your account",
                recipients=["user2@example.com"],
                body="<p>Please click the link to verify.</p>",
                subtype=MessageType.html,
            ),
        ]

        await send_bulk_emails(messages)
        ```
    """
    await fm.send_message(messages)
    return True


"""
================================================================================
MAIL SERVICE USAGE GUIDE
================================================================================

This service provides reusable email sending functions that can be used
throughout the application. All functions are async and return a boolean
indicating success.

INTEGRATION WITH OTHER FEATURES:
---------------------------------

1. Auth Feature - Send welcome emails:
   ```python
   from app.mail.service import send_email_background
   from fastapi import BackgroundTasks

   async def register_user(background_tasks: BackgroundTasks, user_data):
       # ... create user logic ...
       await send_email_background(
           background_tasks=background_tasks,
           recipients=[user_data.email],
           subject="Welcome!",
           body=f"<h1>Welcome {user_data.username}!</h1>"
       )
   ```

2. Users Feature - Send password reset emails:
   ```python
   from app.mail.service import send_email_with_template

   async def send_password_reset(user_email: str, reset_token: str):
       await send_email_with_template(
           recipients=[user_email],
           subject="Password Reset",
           template_name="password_reset.html",
           template_body={"reset_link": f"https://app.com/reset?token={reset_token}"}
       )
   ```

3. Using in Background Tasks:
   Always use `send_email_background()` when sending emails from API endpoints
   to avoid blocking the response. The email will be sent asynchronously.

4. Template-Based Emails:
   Set MAIL_TEMPLATE_FOLDER in settings to enable template support.
   Templates should be Jinja2 files in the specified folder.

5. Error Handling:
   All functions may raise exceptions. Wrap calls in try/except blocks:
   ```python
   try:
       await send_email(...)
   except Exception as e:
       logger.error(f"Failed to send email: {e}")
   ```

CONFIGURATION:
-------------
Mail settings are configured in app.core.config.Settings and can be
set via environment variables:
- MAIL_USERNAME
- MAIL_PASSWORD
- MAIL_FROM
- MAIL_PORT
- MAIL_SERVER
- MAIL_FROM_NAME
- MAIL_STARTTLS
- MAIL_SSL_TLS
- MAIL_USE_CREDENTIALS
- MAIL_VALIDATE_CERTS
- MAIL_TEMPLATE_FOLDER (optional, for Jinja2 templates)

================================================================================
"""

