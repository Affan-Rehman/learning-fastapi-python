# Developer Guide

Quick reference guide for developers working on this FastAPI backend.

## Feature-Based Architecture

This project uses a **feature-based architecture** where each feature is self-contained:

```
app/
├── feature_name/
│   ├── __init__.py
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic models
│   ├── service.py    # Business logic
│   └── router.py     # API endpoints
```

## Quick Checklist: Adding a New Feature

- [ ] Create feature directory: `app/your_feature/`
- [ ] Create `__init__.py` file
- [ ] Define models in `models.py` (if database needed)
- [ ] Define schemas in `schemas.py`
- [ ] Implement service functions in `service.py`
- [ ] Create router endpoints in `router.py`
- [ ] Register router in `app/main.py`
- [ ] Create database migration (if models added)
- [ ] Add permissions (if needed)
- [ ] Update README.md with new endpoints
- [ ] Test endpoints via Swagger UI or curl

## Code Patterns

### Service Function Pattern

```python
async def create_item(db: AsyncSession, item_data: ItemCreate) -> Item:
    """
    Create a new item.
    
    Args:
        db: Database session
        item_data: Item creation data
        
    Returns:
        Created item
    """
    db_item = Item(**item_data.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
```

### Router Endpoint Pattern

```python
@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    item_data: ItemCreate,
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
        
    Raises:
        HTTPException: 400 if validation fails
    """
    return await create_item(db, item_data)
```

### Permission-Based Access

```python
from app.core.dependencies import PermissionChecker

@router.get("/")
async def list_items(
    current_user: User = Depends(PermissionChecker("read_items")),
    db: AsyncSession = Depends(get_db),
):
    # Only users with 'read_items' permission can access
    ...
```

### Rate Limiting

```python
from app.core.rate_limit import get_rate_limit_config, limiter
from starlette.requests import Request

rate_limit_config = get_rate_limit_config()

@router.post("/")
@limiter.limit(rate_limit_config["auth_endpoints"])
async def endpoint(request: Request, ...):
    ...
```

## Database Patterns

### Eager Loading (Prevent N+1)

```python
from sqlalchemy.orm import selectinload

stmt = (
    select(User)
    .options(selectinload(User.role).selectinload(Role.permissions))
    .filter(User.id == user_id)
)
result = await db.execute(stmt)
user = result.scalar_one()
```

### Pagination

```python
skip = 0
limit = 10
stmt = select(Model).offset(skip).limit(limit)
result = await db.execute(stmt)
items = result.scalars().all()
```

### Filtering

```python
from sqlalchemy import or_

if search:
    stmt = stmt.filter(
        or_(
            Model.name.ilike(f"%{search}%"),
            Model.description.ilike(f"%{search}%"),
        )
    )
```

## Email Patterns

### Send Email with Template

```python
from app.mail.service import send_email_with_template

await send_email_with_template(
    recipients=["user@example.com"],
    subject="Email Subject",
    template_name="template.html",
    template_body={"variable": "value"}
)
```

### Send Email in Background

```python
from fastapi import BackgroundTasks
from app.mail.service import send_email_background

@router.post("/")
async def endpoint(
    background_tasks: BackgroundTasks,
    ...
):
    await send_email_background(
        background_tasks=background_tasks,
        recipients=["user@example.com"],
        subject="Subject",
        body="Body"
    )
```

## Error Handling

### Standard Error Responses

```python
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Error message"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unauthorized",
    headers={"WWW-Authenticate": "Bearer"}
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Permission denied"
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)
```

## Testing Patterns

### Test Endpoint with curl

```bash
# POST request
curl -X POST "http://localhost:8000/api/v1/endpoint" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"key": "value"}'

# GET request
curl -X GET "http://localhost:8000/api/v1/endpoint" \
  -H "Authorization: Bearer TOKEN"
```

### Test with Python

```python
import asyncio
from app.your_feature.service import your_function
from app.db.session import get_db

async def test():
    async for db in get_db():
        result = await your_function(db, ...)
        print(result)

asyncio.run(test())
```

## Common Tasks

### Add New Permission

1. Add to database (via migration or manually):
```python
permission = Permission(name="new_permission", description="Description")
db.add(permission)
await db.commit()
```

2. Assign to role:
```python
role.permissions.append(permission)
await db.commit()
```

### Add New Role

```python
role = Role(name="new_role", description="Description")
db.add(role)
await db.commit()
```

### Create Migration

```bash
# Auto-generate
alembic revision --autogenerate -m "Add new table"

# Manual
alembic revision -m "Add new table"
# Then edit the migration file

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Update Environment Variables

1. Add to `app/core/config.py`:
```python
class Settings(BaseSettings):
    NEW_VARIABLE: str = Field(default="default")
```

2. Add to `.env.example`:
```env
NEW_VARIABLE=default_value
```

3. Add to `.env`:
```env
NEW_VARIABLE=your_value
```

## Best Practices

1. **Always use async/await** for database operations
2. **Use eager loading** to prevent N+1 queries
3. **Validate input** with Pydantic schemas
4. **Handle errors** with appropriate HTTP status codes
5. **Document endpoints** with docstrings
6. **Use type hints** for all function parameters and returns
7. **Follow naming conventions**: snake_case for functions, PascalCase for classes
8. **Keep services pure** - no FastAPI dependencies in service layer
9. **Use dependency injection** for database sessions and auth
10. **Test endpoints** via Swagger UI before committing

## File Naming Conventions

- **Models**: `models.py` (SQLAlchemy models)
- **Schemas**: `schemas.py` (Pydantic models)
- **Services**: `service.py` (Business logic)
- **Routers**: `router.py` (API endpoints)
- **Dependencies**: `dependencies.py` (FastAPI dependencies)

## Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
```

## Documentation Standards

### Function Docstrings

```python
async def function_name(param1: str, param2: int) -> ReturnType:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
```

### Endpoint Docstrings

```python
@router.post("/endpoint")
async def endpoint_name(
    data: Schema,
    current_user: User = Depends(get_current_user),
):
    """
    Brief description of the endpoint.
    
    Args:
        data: Request body data
        current_user: Current authenticated user
        
    Returns:
        Response description
        
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 401 if unauthorized
    """
```

## Troubleshooting

### Import Errors

- Ensure `__init__.py` exists in feature directory
- Check import paths are correct
- Verify virtual environment is activated

### Database Errors

- Check database is running: `docker-compose ps`
- Verify `DATABASE_URL` in `.env`
- Check migration status: `alembic current`

### Email Errors

- Verify Gmail App Password (not regular password)
- Check SMTP settings in `.env`
- Test email configuration separately

### Permission Errors

- Verify permission exists in database
- Check user has permission assigned
- Verify `PermissionChecker` is used correctly

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Pydantic**: https://docs.pydantic.dev/
- **Alembic**: https://alembic.sqlalchemy.org/
- **FastAPI-Mail**: https://sabuhish.github.io/fastapi-mail/

