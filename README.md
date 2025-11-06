# FastAPI + Redis + Celery + Supabase Boilerplate

Production-ready FastAPI boilerplate designed for Stage 2 applications (10K+ users) with Redis caching, Celery background job processing, and Supabase backend.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Redis**: Caching layer and rate limiting
- **Celery**: Distributed task queue for background jobs
- **Supabase**: Backend-as-a-Service (Database + Auth + Storage)
- **Pydantic**: Data validation using Python type annotations
- **Docker**: Containerized application with Docker Compose
- **Type Safety**: Full type hints throughout the codebase
- **Error Handling**: Comprehensive exception handling
- **Rate Limiting**: Redis-based rate limiting per IP
- **Caching Strategy**: Cache-aside and write-through patterns
- **Background Tasks**: Email, data processing, and scheduled jobs
- **Health Checks**: Endpoints for monitoring service health

## Project Structure

```
fastapi-redis-celery-supabase/
├── app/
│   ├── api/v1/routes/        # API routes
│   ├── core/                 # Core configuration
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   ├── tasks/                # Celery tasks
│   ├── exceptions/           # Custom exceptions
│   ├── middleware/           # Middleware
│   └── main.py               # Application entry point
├── worker/                   # Celery worker
├── docker/                   # Docker configuration
├── docs/                     # Documentation
└── tests/                    # Tests
```

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Supabase account

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd fastapi-redis-celery-supabase
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start Redis (required)**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or use your local Redis installation
```

6. **Run the application**
```bash
# Start API
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.core.celery_app:celery_app worker --loglevel=info
```

### Docker Deployment

1. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start all services**
```bash
cd docker
docker-compose up -d
```

3. **Check logs**
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

4. **Stop services**
```bash
docker-compose down
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase anon key | Required |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `CELERY_BROKER_URL` | Celery broker URL | redis://localhost:6379/0 |
| `JWT_SECRET` | JWT secret key | Required |
| `API_V1_PREFIX` | API version prefix | /api/v1 |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per IP | 100 |
| `DEFAULT_CACHE_TTL` | Default cache TTL | 3600 |

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user

### Posts
- `GET /api/v1/posts` - List posts (paginated, cached)
- `POST /api/v1/posts` - Create post
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `DELETE /api/v1/posts/{post_id}` - Delete post

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/readiness` - Readiness check
- `GET /api/v1/health/liveness` - Liveness check

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_cache_service.py
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [Caching Strategy](docs/CACHING.md) - Caching patterns and best practices
- [Background Tasks](docs/TASKS.md) - Celery task development guide
- [Scaling Guide](docs/SCALING.md) - Scaling strategies and monitoring

## Development

### Adding a New Route

1. Create route in `app/api/v1/routes/`
2. Add route to router in `app/main.py`
3. Implement business logic in service
4. Add tests

### Adding a New Background Task

1. Create task in `app/tasks/`
2. Add task module to `app/core/celery_app.py`
3. Call task with `.delay()` from routes/services
4. Add tests

### Caching Best Practices

- Use `cache_service.py` for all caching operations
- Cache key format: `{entity}:{id}`
- Set appropriate TTL based on data volatility
- Always have database fallback
- Invalidate cache on updates

## Performance

- **Caching**: Redis-based caching with configurable TTL
- **Rate Limiting**: 100 requests/minute per IP (configurable)
- **Background Jobs**: Celery for async operations
- **Database**: Supabase with connection pooling
- **Horizontal Scaling**: Stateless API for easy scaling

## Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Celery Tasks
```bash
# Check active tasks
celery -A app.core.celery_app:celery_app inspect active

# Check registered tasks
celery -A app.core.celery_app:celery_app inspect registered
```

### Redis Stats
```bash
redis-cli INFO stats
```

## Production Checklist

- [ ] Change `JWT_SECRET` to secure random string
- [ ] Configure proper CORS settings
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Configure log aggregation
- [ ] Set up automated backups
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline
- [ ] Review rate limiting settings

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
# my_fastapi_boilerplate
