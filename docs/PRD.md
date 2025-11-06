# Product Requirements Document (PRD)
## FastAPI + Redis + Celery + Supabase Boilerplate

**Version:** 1.0
**Last Updated:** 2024-11-06
**Owner:** Engineering Team
**Status:** Active

---

## 1. Product Overview

### 1.1 Purpose
Production-ready FastAPI boilerplate designed for Stage 2 applications (10K+ concurrent users) with built-in caching, background job processing, and modern authentication.

### 1.2 Target Audience
- Backend developers building REST APIs
- Startups scaling from MVP to 10K+ users
- Teams needing production-ready architecture
- Developers seeking best practices implementation

### 1.3 Goals
- ✅ Reduce time-to-market for new projects
- ✅ Provide scalable, production-ready foundation
- ✅ Implement industry best practices
- ✅ Enable horizontal scaling
- ✅ Minimize technical debt

---

## 2. Technical Stack

### 2.1 Core Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.104+ | Web framework |
| Supabase | 2.0+ | Backend-as-a-Service (DB + Auth) |
| Redis | 7.0+ | Caching + Rate limiting + Message broker |
| Celery | 5.3+ | Background job processing |
| Pydantic | 2.5+ | Data validation |

### 2.2 Infrastructure
- **Containerization:** Docker + Docker Compose
- **Deployment:** Kubernetes-ready, containerized
- **Monitoring:** Structured logging (JSON)
- **Testing:** Pytest + pytest-asyncio

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization

#### FR-1: User Registration
- **Description:** Users can create new accounts
- **Endpoint:** `POST /api/v1/auth/signup`
- **Input:** Email, password
- **Output:** User data, access token
- **Validation:**
  - Email must be valid format
  - Password minimum 8 characters
- **Side Effects:**
  - Welcome email sent via background job
  - User data cached

#### FR-2: User Login
- **Description:** Existing users can authenticate
- **Endpoint:** `POST /api/v1/auth/login`
- **Input:** Email, password
- **Output:** Access token, refresh token
- **Caching:** Session data cached (1 hour TTL)

#### FR-3: Token Refresh
- **Description:** Refresh expired access tokens
- **Endpoint:** `POST /api/v1/auth/refresh`
- **Input:** Refresh token
- **Output:** New access token

#### FR-4: Logout
- **Description:** Invalidate user session
- **Endpoint:** `POST /api/v1/auth/logout`
- **Side Effects:** Cache invalidation

---

### 3.2 User Management

#### FR-5: Get Current User
- **Description:** Retrieve authenticated user profile
- **Endpoint:** `GET /api/v1/users/me`
- **Authentication:** Required
- **Caching:** User data cached (1 hour TTL)
- **Performance:** < 100ms (cache hit)

#### FR-6: Get User by ID
- **Description:** Retrieve any user profile by ID
- **Endpoint:** `GET /api/v1/users/{user_id}`
- **Authentication:** Required
- **Caching:** User data cached (1 hour TTL)

#### FR-7: Update User Profile
- **Description:** Update authenticated user's profile
- **Endpoint:** `PUT /api/v1/users/{user_id}`
- **Input:** Email, name, etc. (optional fields)
- **Validation:** User can only update own profile
- **Side Effects:** Cache invalidation

---

### 3.3 Content Management (Example)

#### FR-8: Create Post
- **Description:** Create new content post
- **Endpoint:** `POST /api/v1/posts`
- **Authentication:** Required
- **Input:** Title, content, published status
- **Side Effects:**
  - Cache invalidation for post lists
  - Background notification if published

#### FR-9: List Posts (Paginated)
- **Description:** Retrieve paginated list of posts
- **Endpoint:** `GET /api/v1/posts`
- **Query Parameters:**
  - `page` (default: 1)
  - `page_size` (default: 20, max: 100)
  - `published_only` (default: true)
- **Caching:** 30 minutes TTL
- **Performance:** < 200ms

#### FR-10: Get Post by ID
- **Description:** Retrieve single post
- **Endpoint:** `GET /api/v1/posts/{post_id}`
- **Caching:** 30 minutes TTL

#### FR-11: Delete Post
- **Description:** Delete post by ID
- **Endpoint:** `DELETE /api/v1/posts/{post_id}`
- **Authorization:** Only post author
- **Side Effects:** Cache invalidation

---

### 3.4 Health & Monitoring

#### FR-12: Health Check
- **Description:** System health status
- **Endpoint:** `GET /api/v1/health`
- **Output:**
  - Overall status (healthy/degraded)
  - Redis status
  - Supabase status
- **No Authentication Required**
- **No Caching**

#### FR-13: Readiness Check
- **Description:** Service readiness for traffic
- **Endpoint:** `GET /api/v1/health/readiness`
- **Use Case:** Kubernetes readiness probe

#### FR-14: Liveness Check
- **Description:** Service is alive
- **Endpoint:** `GET /api/v1/health/liveness`
- **Use Case:** Kubernetes liveness probe

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (P95) | < 200ms | Application logs |
| API Response Time (P99) | < 500ms | Application logs |
| Cache Hit Rate | > 80% | Redis INFO stats |
| Concurrent Users | 10,000+ | Load testing |
| Requests per Second | 1,000+ | Load testing |

### 4.2 Scalability

#### Horizontal Scaling
- **API Servers:** Stateless, scale independently
- **Celery Workers:** Scale based on queue depth
- **Redis:** Single instance (can cluster later)
- **Database:** Supabase managed (auto-scaling)

#### Resource Limits
- **API Pod:** 4 CPU cores, 8GB RAM
- **Worker Pod:** 2 CPU cores, 4GB RAM
- **Redis:** 2GB memory

### 4.3 Availability
- **Target Uptime:** 99.9% (8.76 hours downtime/year)
- **Recovery Time Objective (RTO):** < 5 minutes
- **Recovery Point Objective (RPO):** < 1 hour

### 4.4 Security

#### Authentication
- JWT-based authentication via Supabase
- Access token expiry: 30 minutes
- Refresh token expiry: 7 days

#### Rate Limiting
- Default: 100 requests/minute per IP
- Sliding window algorithm (Redis-based)
- Returns `429 Too Many Requests` when exceeded

#### Data Protection
- Passwords hashed (Supabase bcrypt)
- Sensitive data not cached
- HTTPS only in production
- CORS properly configured

### 4.5 Reliability

#### Error Handling
- All exceptions logged with context
- Global exception handler
- Structured error responses
- User-friendly error messages

#### Background Jobs
- All tasks idempotent
- Automatic retry (max 3 times)
- Exponential backoff
- Dead letter queue for failed tasks

---

## 5. Data Model

### 5.1 User Entity
```json
{
  "id": "uuid",
  "email": "string (email format)",
  "created_at": "datetime (ISO 8601)",
  "email_confirmed_at": "datetime (ISO 8601) | null"
}
```

### 5.2 Post Entity (Example)
```json
{
  "id": "uuid",
  "title": "string (3-200 chars)",
  "content": "string",
  "published": "boolean",
  "author_id": "uuid",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

---

## 6. API Response Format

### 6.1 Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  }
}
```

### 6.2 Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### 6.3 Paginated Response
```json
{
  "success": true,
  "data": [],
  "page": 1,
  "page_size": 20,
  "total": 100,
  "has_next": true
}
```

---

## 7. Background Jobs

### 7.1 Email Tasks

#### Job: Send Welcome Email
- **Trigger:** User signup
- **Execution:** Asynchronous (Celery)
- **Retry:** 3 attempts, 60s interval
- **Timeout:** 5 minutes
- **Idempotent:** Yes

#### Job: Send Password Reset Email
- **Trigger:** Password reset request
- **Execution:** Asynchronous (Celery)
- **Retry:** 3 attempts, 60s interval

### 7.2 Data Processing Tasks

#### Job: Process User Data
- **Trigger:** Manual/Scheduled
- **Execution:** Asynchronous (Celery)
- **Timeout:** 10 minutes
- **Resource:** CPU-intensive

#### Job: Daily Cleanup
- **Trigger:** Scheduled (2 AM daily)
- **Execution:** Celery Beat
- **Tasks:**
  - Delete logs older than 30 days
  - Archive records older than 90 days
  - Clear expired cache

---

## 8. Caching Strategy

### 8.1 Cache Patterns

| Entity | Pattern | TTL | Key Format |
|--------|---------|-----|------------|
| User | Cache-Aside | 1 hour | `user:{id}` |
| Post | Cache-Aside | 30 min | `post:{id}` |
| Post List | Cache-Aside | 30 min | `posts:page:{n}` |
| Settings | Cache-Aside | 24 hours | `settings:global` |

### 8.2 Cache Invalidation

| Operation | Invalidation Strategy |
|-----------|---------------------|
| Update User | Delete `user:{id}` |
| Delete User | Delete `user:{id}` + pattern `user:{id}:*` |
| Create Post | Invalidate `posts:*` pattern |
| Update Post | Delete `post:{id}` + `posts:*` |

---

## 9. Deployment

### 9.1 Environment Variables
See `.env.example` for full list.

Required:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `REDIS_HOST`
- `JWT_SECRET`

### 9.2 Docker Deployment
```bash
cd docker
docker-compose up -d
```

### 9.3 Kubernetes Deployment
```yaml
# API: 3 replicas
# Workers: 2 replicas
# Redis: 1 replica (StatefulSet)
```

---

## 10. Testing Requirements

### 10.1 Unit Tests
- **Coverage Target:** > 80%
- **Framework:** Pytest
- **Scope:** Services, utilities, models

### 10.2 Integration Tests
- **Framework:** Pytest + TestClient
- **Scope:** API endpoints, database integration

### 10.3 Load Testing
- **Tool:** Locust / k6
- **Scenarios:**
  - 1,000 concurrent users
  - 10,000 requests over 5 minutes
  - Spike test: 0 → 5,000 users in 1 minute

---

## 11. Monitoring & Observability

### 11.1 Logging
- **Format:** JSON (structured logging)
- **Level:** INFO (production), DEBUG (development)
- **Fields:** timestamp, level, message, context

### 11.2 Metrics (Future)
- API request count
- API response time (P50, P95, P99)
- Cache hit rate
- Celery queue length
- Error rate

### 11.3 Alerts (Future)
- API error rate > 1%
- Cache hit rate < 70%
- Celery queue > 1000 tasks
- API response time P99 > 1s

---

## 12. Roadmap

### Version 1.0 (Current)
- ✅ Core API framework
- ✅ Authentication & authorization
- ✅ Caching layer
- ✅ Background jobs
- ✅ Rate limiting
- ✅ Docker deployment

### Version 1.1 (Planned)
- [ ] Metrics & monitoring integration
- [ ] Advanced pagination (cursor-based)
- [ ] File upload/download
- [ ] WebSocket support
- [ ] GraphQL endpoint (optional)

### Version 2.0 (Future)
- [ ] Multi-tenancy support
- [ ] Advanced RBAC (Role-Based Access Control)
- [ ] API versioning (v2)
- [ ] Redis cluster
- [ ] Database read replicas

---

## 13. Success Metrics

### 13.1 Adoption Metrics
- Time to first endpoint: < 1 hour
- Developer satisfaction: > 4/5
- Code reuse rate: > 70%

### 13.2 Technical Metrics
- Zero-downtime deployments: 100%
- Test coverage: > 80%
- Documentation coverage: 100%

---

## 14. Constraints & Assumptions

### 14.1 Constraints
- Python 3.11+ required
- Redis 7.0+ required
- Supabase account required
- Docker for deployment

### 14.2 Assumptions
- Users have basic FastAPI knowledge
- Deployment infrastructure available
- Environment variables properly configured
- Network connectivity to external services

---

## 15. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Redis failure | High | Low | Fallback to DB, cache errors don't break app |
| Supabase outage | High | Low | Use managed service with SLA |
| High load | Medium | Medium | Horizontal scaling, rate limiting |
| Security breach | High | Low | JWT auth, input validation, rate limiting |
| Cache stampede | Medium | Medium | Lock mechanism, staggered TTL |

---

## 16. Appendix

### 16.1 References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/docs/)

### 16.2 Related Documents
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [SCALING.md](./SCALING.md) - Scaling guide
- [CACHING.md](./CACHING.md) - Caching strategy
- [TASKS.md](./TASKS.md) - Background tasks guide
