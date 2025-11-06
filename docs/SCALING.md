# Scaling Guide

## Current Setup (Stage 2)

- Single API instance
- Redis for caching
- Celery workers for background jobs
- Target: 10K+ concurrent users

### Infrastructure
- **API**: 1 instance, 4 CPU cores, 8GB RAM
- **Redis**: 1 instance, 2GB RAM
- **Celery Workers**: 2-4 workers, 2 CPU cores each
- **Database**: Supabase managed

## Metrics to Monitor

### Response Time
- **Target**: P95 < 200ms, P99 < 500ms
- **Monitor**: Application logs, APM tools
- **Action**: If consistently above target, investigate slow queries or add caching

### Cache Hit Rate
- **Target**: >80%
- **Monitor**: Redis INFO stats
- **Action**: If below 70%, review caching strategy

### Task Queue Length
- **Target**: <100 pending tasks
- **Monitor**: Celery inspect commands
- **Action**: If consistently high, add more workers

### Error Rate
- **Target**: <0.1%
- **Monitor**: Application logs, error tracking
- **Action**: Investigate and fix root causes

### Resource Usage
- **API CPU**: Target <70%
- **Redis Memory**: Target <80%
- **Worker CPU**: Target <80%

## Horizontal Scaling

### 1. Add Load Balancer
```yaml
# Example with nginx
upstream fastapi_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://fastapi_backend;
    }
}
```

### 2. Scale API Instances
Since the API is stateless, you can scale horizontally:

```bash
# Docker Compose
docker-compose up --scale api=3
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: fastapi-api:latest
```

### 3. Scale Celery Workers
Add workers based on queue depth:

```bash
# Docker Compose
docker-compose up --scale worker=5
```

Workers can be specialized:
```yaml
# docker-compose.yml
worker-email:
  # ... config ...
  command: celery -A app.core.celery_app worker -Q email

worker-processing:
  # ... config ...
  command: celery -A app.core.celery_app worker -Q processing
```

### 4. Redis Cluster
When single Redis instance becomes a bottleneck:

```yaml
# Redis Cluster setup
redis-1:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes

redis-2:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes

redis-3:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
```

## When to Scale to Stage 3

### Triggers
- Response time > 500ms consistently
- Cache hit rate < 70%
- Task queue backing up (>1000 pending)
- 100K+ concurrent users
- Database queries become bottleneck

### Stage 3 Changes
- **Database**: Read replicas, connection pooling
- **Redis**: Redis Cluster with multiple nodes
- **API**: Auto-scaling based on CPU/memory
- **CDN**: Add CDN for static assets
- **Monitoring**: Comprehensive APM (Datadog, New Relic)

## Bottleneck Identification

### Slow Endpoints
**Symptom**: Specific endpoints have high response time

**Solutions**:
1. Add caching
2. Optimize database queries
3. Add database indexes
4. Move heavy processing to background tasks

```python
# Before
@router.get("/slow-endpoint")
async def slow_endpoint():
    result = heavy_computation()
    return result

# After
@router.get("/fast-endpoint")
async def fast_endpoint():
    task = heavy_computation.delay()
    return {"task_id": task.id, "status": "processing"}
```

### High Task Queue
**Symptom**: Celery queue has many pending tasks

**Solutions**:
1. Add more workers
2. Optimize task code
3. Batch operations
4. Implement task priorities

```python
# High priority task
send_email.apply_async(args=[...], priority=10)

# Low priority task
cleanup_data.apply_async(args=[...], priority=1)
```

### Redis CPU High
**Symptom**: Redis CPU usage > 80%

**Solutions**:
1. Implement Redis Cluster
2. Reduce key scanning operations
3. Use pipeline for batch operations
4. Review cache key patterns

```python
# Use pipeline for batch operations
pipe = redis_client.pipeline()
for key, value in items:
    pipe.set(key, value)
await pipe.execute()
```

### Database Bottleneck
**Symptom**: Slow database queries, high connection count

**Solutions**:
1. Add database indexes
2. Implement connection pooling
3. Use read replicas
4. Optimize N+1 queries
5. Add more aggressive caching

## Cost Optimization

### 1. Auto-scaling
Scale down during low-traffic periods:

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-api
spec:
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### 2. Cache Effectively
Better caching = less database load = lower costs

### 3. Batch Operations
Reduce API calls by batching:

```python
# Instead of N API calls
for user_id in user_ids:
    await process_user(user_id)

# Batch in single background task
await process_users_batch.delay(user_ids)
```

### 4. Use CDN
Offload static assets and reduce API load

## Performance Testing

### Load Testing with Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_posts(self):
        self.client.get("/api/v1/posts")

    @task
    def health_check(self):
        self.client.get("/api/v1/health")
```

Run test:
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=1000 --spawn-rate=10
```

### Benchmarking
```bash
# Apache Bench
ab -n 10000 -c 100 http://localhost:8000/api/v1/health

# wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/posts
```

## Deployment Strategy

### Blue-Green Deployment
1. Deploy new version (green)
2. Run health checks
3. Switch traffic from blue to green
4. Keep blue running for quick rollback

### Canary Deployment
1. Deploy new version to small subset (10%)
2. Monitor metrics
3. Gradually increase traffic
4. Rollback if issues detected

### Rolling Update
1. Update instances one by one
2. Wait for health check
3. Continue to next instance
