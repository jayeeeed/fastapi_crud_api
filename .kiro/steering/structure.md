# Project Structure

## File Organization

### Core Application Files
- `main.py` - Production FastAPI application with full CRUD endpoints
- `dev.py` - Development version with ngrok integration
- `test.py` - Test/experimental version with additional features
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic data validation schemas
- `database.py` - Database connection and session management
- `health.py` - Health monitoring and automated ping functionality

### Configuration & Data
- `.env` - Environment variables (DATABASE_URL, etc.)
- `requirements.txt` - Python dependencies
- `items.db` - Local SQLite database file (if used)

### Development Files
- `.gitignore` - Git ignore patterns
- `.venv/` - Python virtual environment
- `__pycache__/` - Python bytecode cache

## Architecture Patterns

### Layered Architecture
- **API Layer**: FastAPI routes and endpoints
- **Schema Layer**: Pydantic models for request/response validation
- **Business Logic**: Embedded in route handlers
- **Data Layer**: SQLAlchemy models and database operations

### Code Organization Conventions
- Database models in `models.py` using SQLAlchemy declarative base
- API schemas in `schemas.py` using Pydantic BaseModel
- Database session dependency injection pattern
- Consistent error handling with HTTPException
- CORS middleware configuration for cross-origin requests

### Naming Conventions
- Snake_case for Python variables and functions
- PascalCase for Pydantic and SQLAlchemy model classes
- RESTful endpoint naming (`/items/`, `/items/{item_id}`)
- Consistent response models across endpoints