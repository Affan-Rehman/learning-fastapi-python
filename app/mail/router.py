from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi_mail import MessageSchema, MessageType
from starlette.requests import Request

from app.core.dependencies import PermissionChecker
from app.core.rate_limit import get_rate_limit_config, limiter
from app.mail.schemas import (
    BulkEmailSchema,
    EmailMultipartSchema,
    EmailSchema,
    EmailWithAttachmentSchema,
    EmailWithTemplateSchema,
)
from app.mail.service import (
    send_bulk_emails,
    send_email,
    send_email_background,
    send_email_with_attachments,
    send_email_with_template,
    send_multipart_email,
)
from app.users.models import User

router = APIRouter()
rate_limit_config = get_rate_limit_config()


@router.post("/email", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_endpoint(
    request: Request,
    email_data: EmailSchema,
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send a standard email.

    Args:
        email_data: Email data including recipients and optional body
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        html_body = email_data.body.get("html", "<p>Hi, thanks for using Fastapi-mail</p>") if email_data.body else "<p>Hi, thanks for using Fastapi-mail</p>"
        await send_email(
            recipients=email_data.email,
            subject="Fastapi-Mail module",
            body=html_body,
            subtype=MessageType.html,
        )
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post("/email/background", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_background_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    email_data: EmailSchema,
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send email as a background task.

    Args:
        background_tasks: FastAPI background tasks
        email_data: Email data including recipients and optional body
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        body = email_data.body.get("text", "Simple background task") if email_data.body else "Simple background task"
        await send_email_background(
            background_tasks=background_tasks,
            recipients=email_data.email,
            subject="Fastapi mail module",
            body=body,
            subtype=MessageType.plain,
        )
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post("/email/template", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_template_endpoint(
    request: Request,
    email_data: EmailWithTemplateSchema,
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send email using Jinja2 template.

    Args:
        email_data: Email data with template name and template variables
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        await send_email_with_template(
            recipients=email_data.email,
            subject="Fastapi-Mail module",
            template_name=email_data.template_name,
            template_body=email_data.body,
        )
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post("/email/attachment", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_attachment_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    email: str = Form(...),
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send email with file attachment.

    Args:
        background_tasks: FastAPI background tasks
        file: File to attach
        email: Recipient email address
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        await send_email_background(
            background_tasks=background_tasks,
            recipients=[email],
            subject="Fastapi mail module",
            body="Email with attachment",
            subtype=MessageType.html,
            attachments=[file],
        )
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post("/email/multipart", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_multipart_endpoint(
    request: Request,
    email_data: EmailMultipartSchema,
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send multipart email (HTML + plain text).

    Args:
        email_data: Email data with HTML and plain text content
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        await send_multipart_email(
            recipients=email_data.email,
            subject=email_data.subject,
            html_body=email_data.html_body,
            plain_text_body=email_data.plain_text_body,
        )
        return JSONResponse(status_code=200, content={"message": "email has been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post("/email/bulk", status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["authenticated"])
async def send_email_bulk_endpoint(
    request: Request,
    email_data: BulkEmailSchema,
    current_user: User = Depends(PermissionChecker("send_email")),
) -> JSONResponse:
    """
    Send multiple emails using a single SMTP connection.

    Args:
        email_data: List of email schemas to send
        current_user: Current authenticated user with send_email permission

    Returns:
        JSON response with success message
    """
    try:
        messages = []
        for email_item in email_data.emails:
            body = email_item.body.get("html", "<p>Bulk email</p>") if email_item.body else "<p>Bulk email</p>"
            message = MessageSchema(
                subject="Fastapi-Mail module",
                recipients=email_item.email,
                body=body,
                subtype=MessageType.html,
            )
            messages.append(message)

        await send_bulk_emails(messages)
        return JSONResponse(status_code=200, content={"message": "emails have been sent"})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send emails: {str(e)}",
        )

