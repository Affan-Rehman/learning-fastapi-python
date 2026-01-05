# FastAPI Backend with RBAC

A production-ready FastAPI backend with JWT authentication, Role-Based Access Control (RBAC), email functionality, password reset, and Docker setup for local development.

## Features

- ✅ **FastAPI** with async/await support
- ✅ **JWT Authentication** with access tokens
- ✅ **Password Reset Flow** with email notifications
- ✅ **Password Change** with old password verification
- ✅ **Email Service** with Jinja2 templates
- ✅ **RBAC System** with roles and permissions
- ✅ **Async SQLAlchemy** with asyncpg driver
- ✅ **Alembic Migrations** with async support
- ✅ **Rate Limiting** with slowapi
- ✅ **Docker Compose** for local development
- ✅ **Feature-Based Architecture** for scalability
- ✅ **Optimized Queries** with proper indexing
- ✅ **No N+1 Problems** with eager loading

## Project Structure

This project follows a **feature-based architecture** where each feature is self-contained:

```
/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Global configuration and shared utilities
│   │   ├── config.py        # Application settings
│   │   ├── dependencies.py  # Shared dependencies (PermissionChecker, RoleChecker)
│   │   ├── rate_limit.py    # Rate limiting configuration
│   │   ├── security.py      # Password hashing, JWT tokens
│   │   └── query_params.py  # Shared query parameter models
│   ├── db/                  # Database configuration
│   │   ├── base.py          # Base model class
│   │   ├── session.py       # Database session management
│   │   └── migrations/      # Alembic migration scripts
│   ├── auth/                # Authentication Feature
│   │   ├── router.py        # Auth endpoints (login, register, password reset)
│   │   ├── service.py       # Auth business logic
│   │   ├── schemas.py       # Auth Pydantic models
│   │   └── dependencies.py  # get_current_user dependency
│   ├── users/               # User Management Feature
│   │   ├── router.py        # User CRUD endpoints
│   │   ├── service.py       # User business logic
│   │   ├── models.py        # User SQLAlchemy model
│   │   └── schemas.py       # User Pydantic models
│   ├── rbac/                # RBAC Feature
│   │   ├── router.py        # Roles and permissions endpoints
│   │   ├── service.py       # RBAC business logic
│   │   ├── models.py        # Role and Permission models
│   │   └── schemas.py       # RBAC Pydantic models
│   └── mail/                # Email Feature
│       ├── router.py        # Email sending endpoints
│       ├── service.py        # Email service functions
│       ├── schemas.py       # Email Pydantic models
│       ├── config.py        # Email configuration
│       └── templates/       # Jinja2 email templates
│           ├── base_template.html
│           ├── password_reset.html
│           ├── password_reset_success.html
│           └── password_change_success.html
├── alembic/                 # Database migrations
├── docker-compose.yml       # Local development setup
├── Dockerfile              # Container image
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variables template
```

## Quick Start

### Prerequisites

- **Python 3.11, 3.12, or 3.14** (asyncpg 0.31.0+ supports Python 3.14)
- Docker and Docker Compose
- PostgreSQL (via Docker Compose)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd learning
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and configure the following:

**Required Settings:**
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration (default: 30)
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`: Reset token expiration (default: 30)
- `FRONTEND_URL`: Frontend URL for password reset links

**Email Configuration (Gmail Example):**
- `MAIL_USERNAME`: Your Gmail address
- `MAIL_PASSWORD`: Gmail App Password (see [Email Setup](#email-setup))
- `MAIL_FROM`: Sender email address
- `MAIL_SERVER`: `smtp.gmail.com`
- `MAIL_PORT`: `587`
- `MAIL_FROM_NAME`: Display name for emails

See `.env.example` for all available options.

### 3. Start Database

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Adminer (database UI) on port 8080

### 4. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
alembic upgrade head
```

This creates all tables and seeds RBAC data (roles, permissions).

### 6. Start Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Adminer**: http://localhost:8080

## Email Setup

### Gmail Configuration

Gmail requires an **App Password** (not your regular password) for SMTP access:

1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Generate and copy the 16-character password
5. Add it to `.env` as `MAIL_PASSWORD` (remove spaces)

**Example:**
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcdefghijklmnop  # 16-character app password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
```

### Other Email Providers

For other providers, update the SMTP settings in `.env`:
- **Outlook**: `smtp-mail.outlook.com`, port 587
- **SendGrid**: `smtp.sendgrid.net`, port 587
- **Custom SMTP**: Configure according to your provider's documentation

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|-----------|-------------|---------------|
| POST | `/register` | Register new user | ❌ |
| POST | `/login` | Login and get JWT token | ❌ |
| GET | `/me` | Get current user info | ✅ |
| POST | `/forgot-password` | Request password reset email | ❌ |
| POST | `/reset-password` | Reset password with token | ❌ |
| POST | `/change-password` | Change password (requires old password) | ✅ |

### Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required | Permission Required |
|--------|-----------|-------------|---------------|---------------------|
| GET | `/me` | Get current user | ✅ | - |
| GET | `/{user_id}` | Get user by ID | ✅ | `read_user` |
| GET | `/` | List users (paginated) | ✅ | `read_user` |
| PUT | `/{user_id}` | Update user | ✅ | `update_user` |
| DELETE | `/{user_id}` | Delete user | ✅ | `delete_user` |

### RBAC (`/api/v1/rbac`)

| Method | Endpoint | Description | Auth Required | Permission Required |
|--------|-----------|-------------|---------------|---------------------|
| GET | `/roles` | List roles (paginated) | ✅ | `manage_roles` |
| GET | `/permissions` | List permissions (paginated) | ✅ | `manage_roles` |

### Mail (`/api/v1/mail`)

| Method | Endpoint | Description | Auth Required | Permission Required |
|--------|-----------|-------------|---------------|---------------------|
| POST | `/email` | Send standard email | ✅ | `send_email` |
| POST | `/email/background` | Send email as background task | ✅ | `send_email` |
| POST | `/email/template` | Send email with Jinja2 template | ✅ | `send_email` |
| POST | `/email/attachment` | Send email with attachment | ✅ | `send_email` |
| POST | `/email/multipart` | Send multipart email (HTML + text) | ✅ | `send_email` |
| POST | `/email/bulk` | Send multiple emails | ✅ | `send_email` |

### Health (`/api/v1/health`)

| Method | Endpoint | Description | Auth Required |
|--------|-----------|-------------|---------------|
| GET | `/health` | Health check | ❌ |

## Using the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"
```

### 3. Use JWT Token

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Request Password Reset

```bash
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent."
}
```

### 5. Reset Password

```bash
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL",
    "new_password": "NewSecurePass123!"
  }'
```

### 6. Change Password (Authenticated)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "CurrentPass123!",
    "new_password": "NewSecurePass123!"
  }'
```

## RBAC System

### Default Roles

- **admin**: All permissions
- **user**: `read_user` (own profile)
- **moderator**: `read_user`, `update_user`

### Default Permissions

- `create_user` - Create new users
- `read_user` - Read user information
- `update_user` - Update user information
- `delete_user` - Delete users
- `manage_roles` - Manage roles and permissions
- `send_email` - Send emails

### Using Permissions in Endpoints

```python
from app.core.dependencies import PermissionChecker

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(PermissionChecker("read_user"))
):
    # Only users with 'read_user' permission can access
    return {"message": "Access granted"}
```

## How to Add a New Feature

This project follows a **feature-based architecture**. Here's a step-by-step guide to add a new feature:

### Step 1: Create Feature Directory

Create a new directory under `app/` for your feature:

```bash
mkdir -p app/your_feature
touch app/your_feature/__init__.py
```

### Step 2: Create Feature Files

Each feature should have these files:

```
app/your_feature/
├── __init__.py
├── models.py       # SQLAlchemy models (if database tables needed)
├── schemas.py      # Pydantic models for request/response
├── service.py      # Business logic
└── router.py       # API endpoints
```

### Step 3: Define Models (if needed)

If your feature needs database tables, create models in `models.py`:

```python
# app/your_feature/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Step 4: Define Schemas

Create Pydantic models for request/response validation:

```python
# app/your_feature/schemas.py
from pydantic import BaseModel
from datetime import datetime

class YourModelCreate(BaseModel):
    name: str

class YourModelResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 5: Implement Service Layer

Add business logic in `service.py`:

```python
# app/your_feature/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.your_feature.models import YourModel
from app.your_feature.schemas import YourModelCreate

async def create_item(db: AsyncSession, item_data: YourModelCreate) -> YourModel:
    """
    Create a new item.
    
    Args:
        db: Database session
        item_data: Item creation data
        
    Returns:
        Created item
    """
    db_item = YourModel(**item_data.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_item(db: AsyncSession, item_id: int) -> YourModel | None:
    """
    Get item by ID.
    
    Args:
        db: Database session
        item_id: Item ID
        
    Returns:
        Item if found, None otherwise
    """
    stmt = select(YourModel).filter(YourModel.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

### Step 6: Create Router

Define API endpoints in `router.py`:

```python
# app/your_feature/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.your_feature.schemas import YourModelCreate, YourModelResponse
from app.your_feature.service import create_item, get_item
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User

router = APIRouter()

@router.post("/", response_model=YourModelResponse, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    item_data: YourModelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new item.
    
    Args:
        item_data: Item creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created item
    """
    return await create_item(db, item_data)

@router.get("/{item_id}", response_model=YourModelResponse)
async def get_item_endpoint(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get item by ID.
    
    Args:
        item_id: Item ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Item information
        
    Raises:
        HTTPException: 404 if item not found
    """
    item = await get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

### Step 7: Register Router in main.py

Add your router to `app/main.py`:

```python
# app/main.py
from app.your_feature.router import router as your_feature_router

# ... existing code ...

app.include_router(
    your_feature_router,
    prefix=f"{settings.API_V1_PREFIX}/your-feature",
    tags=["your-feature"]
)
```

### Step 8: Create Database Migration

If you added new models, create a migration:

```bash
alembic revision --autogenerate -m "Add your_feature table"
alembic upgrade head
```

### Step 9: Add Permissions (if needed)

If your feature needs permission-based access:

1. Add permission to database (via migration or manually):
```python
# In a migration or seed script
permission = Permission(name="manage_your_feature", description="Manage your feature")
db.add(permission)
```

2. Use in router:
```python
from app.core.dependencies import PermissionChecker

@router.post("/")
async def create_item(
    current_user: User = Depends(PermissionChecker("manage_your_feature")),
    ...
):
    ...
```

### Step 10: Document Your Feature

Add documentation:
- Update this README with your new endpoints
- Add docstrings to all functions
- Update API tags and descriptions

### Example: Complete Feature Structure

```
app/notifications/
├── __init__.py
├── models.py          # Notification model
├── schemas.py         # NotificationCreate, NotificationResponse
├── service.py         # create_notification, get_notifications, etc.
└── router.py          # POST /notifications, GET /notifications, etc.
```

## Development

### Code Formatting

```bash
black .
```

### Linting

```bash
ruff check .
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Docker Development

### Build and Run

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

### Stop Services

```bash
docker-compose down
```

## Environment Variables

See `.env.example` for all available variables. Key variables:

### Application
- `PROJECT_NAME`: Application name
- `VERSION`: Application version
- `ENVIRONMENT`: `development`, `staging`, or `production`
- `API_V1_PREFIX`: API prefix (default: `/api/v1`)

### Security
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration (default: `30`)
- `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`: Reset token expiration (default: `30`)

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `DB_POOL_SIZE`: Connection pool size (default: `20`)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: `10`)

### CORS
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `FRONTEND_URL`: Frontend URL for password reset links

### Rate Limiting
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: `true`)
- `RATE_LIMIT_AUTHENTICATED`: Requests per minute for authenticated users (default: `100`)
- `RATE_LIMIT_UNAUTHENTICATED`: Requests per minute for unauthenticated users (default: `20`)
- `RATE_LIMIT_AUTH_ENDPOINTS`: Requests per minute for auth endpoints (default: `5`)

### Email
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password (Gmail App Password)
- `MAIL_FROM`: Sender email address
- `MAIL_SERVER`: SMTP server address
- `MAIL_PORT`: SMTP port (default: `587`)
- `MAIL_FROM_NAME`: Sender display name
- `MAIL_STARTTLS`: Enable STARTTLS (default: `true`)
- `MAIL_SSL_TLS`: Enable SSL/TLS (default: `false`)

## Database

### Connection

The app uses async SQLAlchemy with asyncpg driver for optimal performance.

### Migrations

Migrations are managed with Alembic. The initial migration creates:
- Users table with indexes
- Roles table with indexes
- Permissions table with indexes
- Roles-Permissions junction table with composite key

### Indexes

All frequently queried fields are indexed:
- `users.email` (unique)
- `users.username` (unique)
- `users.role_id` (foreign key)
- `roles.name` (unique)
- `permissions.name` (unique)
- `roles_permissions` (composite primary key)

## Security

- **Password Hashing**: bcrypt with passlib
- **JWT Tokens**: python-jose with HS256 algorithm
- **Rate Limiting**: slowapi with in-memory storage
- **CORS**: Configurable allowed origins
- **Input Validation**: Pydantic schemas
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Email Enumeration Protection**: Forgot password always returns success

## Performance

- **Async Operations**: All database operations are async
- **Connection Pooling**: Configurable pool size
- **Eager Loading**: Prevents N+1 query problems
- **Indexed Queries**: All filtered/sorted fields indexed
- **Query Optimization**: Efficient pagination and filtering

## Email Templates

Email templates use Jinja2 and are located in `app/mail/templates/`:

- `base_template.html`: Base template with header, footer, and styling
- `password_reset.html`: Password reset email
- `password_reset_success.html`: Confirmation after password reset
- `password_change_success.html`: Confirmation after password change

### Creating Custom Email Templates

1. Create a new template in `app/mail/templates/`:
```html
{% extends "base_template.html" %}

{% block title %}Your Email Title{% endblock %}

{% block header %}Your Header{% endblock %}

{% block content %}
    <p>Your email content here</p>
    <p>Variable: {{ variable_name }}</p>
{% endblock %}
```

2. Use in service:
```python
from app.mail.service import send_email_with_template

await send_email_with_template(
    recipients=["user@example.com"],
    subject="Your Subject",
    template_name="your_template.html",
    template_body={"variable_name": "value"}
)
```

## Documentation

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

All endpoints are documented with Google-style docstrings.

## Troubleshooting

### Email Not Sending

1. **Gmail App Password**: Ensure you're using a Gmail App Password, not your regular password
2. **2FA Enabled**: Gmail requires 2-Factor Authentication to generate App Passwords
3. **Check Logs**: Check server logs for SMTP connection errors
4. **Test Connection**: Use the test script to verify email configuration

### Database Connection Issues

1. **Docker Running**: Ensure Docker Compose is running: `docker-compose ps`
2. **Connection String**: Verify `DATABASE_URL` in `.env`
3. **Port Conflicts**: Ensure port 5432 is not in use by another service

### Migration Errors

1. **Database State**: Check current migration: `alembic current`
2. **Rollback**: If needed: `alembic downgrade -1`
3. **Fresh Start**: Drop and recreate database if needed

## Contributing

1. Follow the feature-based architecture
2. Add comprehensive docstrings
3. Include error handling
4. Write tests for new features
5. Update this README with new endpoints

## License

[Your License Here]
