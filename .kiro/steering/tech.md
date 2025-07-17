# Technology Stack

## Core Framework & Libraries
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application
- **PostgreSQL**: Primary database (Neon hosted)

## Additional Dependencies
- **python-dotenv**: Environment variable management
- **psycopg2-binary**: PostgreSQL adapter
- **httpx**: HTTP client for health checks
- **APScheduler**: Background task scheduling
- **pyngrok**: Development tunneling (dev environment only)

## Common Commands

### Development
```bash
# Run development server with ngrok
python dev.py

# Run production server
python main.py

# Run test server
python test.py
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Database
- Database migrations handled automatically via SQLAlchemy metadata
- Connection configured via `DATABASE_URL` environment variable
- Uses PostgreSQL hosted on Neon platform