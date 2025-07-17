# Design Document

## Overview

This design enhances the existing FastAPI CRUD application by implementing a layered architecture with comprehensive error handling, validation, logging, search capabilities, and security features. The design maintains backward compatibility while adding production-ready features including request/response middleware, structured logging, input validation, and database optimization.

## Architecture

### Current Architecture Analysis
The existing application follows a simple three-layer pattern:
- **Presentation Layer**: FastAPI endpoints in `main.py`
- **Data Layer**: SQLAlchemy models in `models.py` and database configuration in `database.py`
- **Schema Layer**: Pydantic schemas in `schemas.py`

### Enhanced Architecture
The enhanced architecture will maintain the existing structure while adding:

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  Middleware Layer                                           │
│  ├── Request Logging Middleware                             │
│  ├── Error Handling Middleware                              │
│  ├── Rate Limiting Middleware                               │
│  └── Security Headers Middleware                            │
├─────────────────────────────────────────────────────────────┤
│  API Layer (Enhanced Endpoints)                             │
│  ├── CRUD Operations with Validation                        │
│  ├── Search and Filter Endpoints                            │
│  └── Enhanced Error Responses                               │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (New)                                        │
│  ├── Item Service (Business Logic)                          │
│  ├── Search Service                                         │
│  └── Validation Service                                     │
├─────────────────────────────────────────────────────────────┤
│  Data Access Layer (Enhanced)                               │
│  ├── Enhanced Database Configuration                        │
│  ├── Connection Pooling                                     │
│  └── Transaction Management                                 │
├─────────────────────────────────────────────────────────────┤
│  Utilities Layer (New)                                      │
│  ├── Logging Configuration                                  │
│  ├── Response Formatters                                    │
│  └── Exception Handlers                                     │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Enhanced Schemas (`schemas.py`)

**Enhanced Validation Models:**
```python
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    price: int = Field(..., ge=0, description="Item price in cents")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[int] = Field(None, ge=0)

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

class SearchParams(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: str
    timestamp: datetime
```

### 2. Service Layer (`services/`)

**Item Service (`services/item_service.py`):**
- Encapsulates business logic for item operations
- Handles validation and data transformation
- Manages database transactions
- Provides search and filtering capabilities

**Search Service (`services/search_service.py`):**
- Implements search algorithms
- Handles query optimization
- Manages search parameter validation

### 3. Middleware Components (`middleware/`)

**Logging Middleware (`middleware/logging.py`):**
- Logs all incoming requests and outgoing responses
- Captures request duration and status codes
- Implements structured logging with correlation IDs

**Error Handling Middleware (`middleware/error_handler.py`):**
- Catches and formats all application exceptions
- Provides consistent error response format
- Logs errors with appropriate severity levels

**Rate Limiting Middleware (`middleware/rate_limiter.py`):**
- Implements token bucket algorithm
- Configurable rate limits per endpoint
- Returns appropriate HTTP 429 responses

**Security Middleware (`middleware/security.py`):**
- Adds security headers (HSTS, CSP, etc.)
- Implements request sanitization
- Handles CORS configuration

### 4. Enhanced Database Layer (`database.py`)

**Connection Pool Configuration:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Transaction Management:**
- Automatic rollback on exceptions
- Connection cleanup
- Retry logic for transient failures

### 5. Utilities (`utils/`)

**Logger Configuration (`utils/logger.py`):**
- Structured JSON logging
- Multiple log levels and handlers
- Request correlation tracking

**Response Formatters (`utils/responses.py`):**
- Standardized success/error response formats
- Metadata injection (timestamps, request IDs)
- Pagination helpers

## Data Models

### Enhanced Item Model
```python
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_name_price', 'name', 'price'),
        Index('idx_price_range', 'price'),
    )
```

### Database Indexes
- Primary index on `id` (existing)
- Composite index on `name` and `price` for search optimization
- Range index on `price` for price filtering
- Text index on `name` for name searching

## Error Handling

### Exception Hierarchy
```python
class ItemManagementException(Exception):
    """Base exception for item management operations"""
    pass

class ItemNotFoundError(ItemManagementException):
    """Raised when an item is not found"""
    pass

class ValidationError(ItemManagementException):
    """Raised when input validation fails"""
    pass

class DatabaseError(ItemManagementException):
    """Raised when database operations fail"""
    pass
```

### Error Response Format
```json
{
    "error": "ValidationError",
    "detail": "Item name must be between 1 and 100 characters",
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z",
    "field_errors": {
        "name": ["String too short"]
    }
}
```

### HTTP Status Code Mapping
- 400: Bad Request (validation errors)
- 404: Not Found (item not found)
- 422: Unprocessable Entity (schema validation)
- 429: Too Many Requests (rate limiting)
- 500: Internal Server Error (unexpected errors)
- 503: Service Unavailable (database connection issues)

## Testing Strategy

### Unit Testing
- **Models**: Test validation, constraints, and relationships
- **Services**: Test business logic and error handling
- **Utilities**: Test logging, formatting, and helper functions

### Integration Testing
- **API Endpoints**: Test complete request/response cycles
- **Database Operations**: Test CRUD operations and transactions
- **Middleware**: Test request processing pipeline

### Performance Testing
- **Load Testing**: Test concurrent request handling
- **Database Performance**: Test query optimization and connection pooling
- **Rate Limiting**: Test rate limit enforcement

### Test Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_middleware.py
└── performance/
    ├── test_load.py
    └── test_rate_limits.py
```

### Testing Tools
- **pytest**: Primary testing framework
- **pytest-asyncio**: For async test support
- **httpx**: For API testing
- **factory_boy**: For test data generation
- **pytest-cov**: For coverage reporting

## API Enhancements

### New Endpoints
```
GET /items/search?name={name}&min_price={min}&max_price={max}
GET /items/stats (item count, price statistics)
GET /health/detailed (enhanced health check)
```

### Enhanced Existing Endpoints
- Add request/response logging
- Implement proper error handling
- Add input validation
- Include response metadata

### OpenAPI Documentation
- Comprehensive endpoint descriptions
- Request/response examples
- Error response documentation
- Authentication requirements (future)

## Security Considerations

### Input Validation
- SQL injection prevention through parameterized queries
- XSS prevention through input sanitization
- Length limits on all string inputs
- Type validation for all numeric inputs

### Security Headers
```python
security_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

### Rate Limiting Strategy
- 100 requests per minute per IP for general endpoints
- 10 requests per minute per IP for write operations
- Configurable limits based on endpoint sensitivity

## Performance Optimizations

### Database Optimizations
- Connection pooling with appropriate pool sizes
- Query optimization with proper indexes
- Lazy loading for related data
- Database query logging and monitoring

### Caching Strategy
- Response caching for read-heavy endpoints
- Database query result caching
- Cache invalidation on data updates

### Monitoring and Metrics
- Request duration tracking
- Database query performance monitoring
- Error rate monitoring
- Rate limit hit tracking