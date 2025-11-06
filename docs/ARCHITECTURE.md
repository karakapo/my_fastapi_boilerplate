# Architecture Overview

## System Components

- **FastAPI**: REST API layer
- **Redis**: Caching + Rate limiting + Celery broker
- **Celery**: Background job processing
- **Supabase**: Database + Auth + Storage

## Data Flow

1. Request → FastAPI Route
2. Route → Service (business logic)
3. Service → Check Redis cache
4. If cache miss → Supabase query → Cache result
5. Heavy operations → Celery task

## Layer Responsibilities

### Routes (`app/api/v1/routes/`)
- HTTP handling, validation
- Request/response transformation
- Authentication/authorization checks
- Minimal business logic

### Services (`app/services/`)
- Business logic implementation
- Caching strategy
- Database operations
- Service-to-service communication

### Tasks (`app/tasks/`)
- Async/background operations
- Scheduled jobs
- Long-running processes
- Idempotent operations

### Core (`app/core/`)
- Shared utilities
- Configuration management
- Database/Redis/Celery clients
- Security utilities

## Scalability

### Current Setup (Stage 2)
- Stateless API (horizontal scaling ready)
- Redis for distributed caching
- Celery workers scale independently
- Target: 10K+ concurrent users

### Horizontal Scaling
- API instances can be scaled independently
- Workers can be scaled based on queue depth
- Redis can be clustered for higher throughput
- Load balancer distributes traffic across API instances

## Security

- JWT-based authentication via Supabase
- Rate limiting per IP address
- Input validation with Pydantic
- Error handling without information leakage

## Caching Strategy

- Cache-aside pattern for reads
- Write-through pattern for updates
- Automatic cache invalidation on updates
- Configurable TTL per entity type

## Background Jobs

- Email notifications
- Data processing
- Report generation
- Scheduled cleanup tasks
