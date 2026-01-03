# FastAPI Backend with RBAC

A FastAPI backend with JWT authentication, Role-Based Access Control (RBAC), database migrations, and Docker setup for local development.

## Features

- ✅ **FastAPI** with async/await support
- ✅ **JWT Authentication** with access tokens
- ✅ **RBAC System** with roles and permissions
- ✅ **Async SQLAlchemy** with asyncpg driver
- ✅ **Alembic Migrations** with async support
- ✅ **Rate Limiting** with slowapi
- ✅ **Docker Compose** for local development
- ✅ **CI Pipeline** with GitHub Actions (linting, formatting, testing)
- ✅ **Comprehensive Testing** setup
- ✅ **Optimized Queries** with proper indexing
- ✅ **No N+1 Problems** with eager loading

## Project Structure

```
/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── core/                # Configuration, security, dependencies
│   ├── crud/                # Business logic
│   ├── db/                  # Database session and base
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── docker-compose.yml       # Local development setup
├── Dockerfile               # Container image
└── requirements.txt         # Python dependencies
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

Edit `.env` and update the following:

- Generate a secret key: `openssl rand -hex 32`
- Update `DATABASE_URL` if needed
- Configure CORS origins for your frontend

### 3. Start Database

```bash
docker-compose up -d
```

This starts:

- PostgreSQL on port 5432
- Adminer (database UI) on port 8080

### 4. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Adminer: http://localhost:8080

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Users (Protected)

- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{id}` - Get user by ID (requires `read_user`)
- `GET /api/v1/users` - List users with pagination/filtering (requires `read_user`)
- `PUT /api/v1/users/{id}` - Update user (requires `update_user`)
- `DELETE /api/v1/users/{id}` - Delete user (requires `delete_user`)

### RBAC (Admin Only)

- `GET /api/v1/rbac/roles` - List roles (requires `manage_roles`)
- `GET /api/v1/rbac/permissions` - List permissions (requires `manage_roles`)

### Health

- `GET /api/v1/health/health` - Health check

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

## Development

### Running Tests

```bash
pytest
```

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
alembic revision --autogenerate -m "description"
alembic upgrade head
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

See `.env.example` for all required variables. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS`: Allowed frontend origins
- `RATE_LIMIT_*`: Rate limiting configuration

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

## Performance

- **Async Operations**: All database operations are async
- **Connection Pooling**: Configurable pool size
- **Eager Loading**: Prevents N+1 query problems
- **Indexed Queries**: All filtered/sorted fields indexed
- **Query Optimization**: Efficient pagination and filtering

## Documentation

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

All endpoints are documented with Google-style docstrings.
