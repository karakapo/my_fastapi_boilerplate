# Deployment Guide

## Table of Contents
1. [Docker Deployment](#docker-deployment)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Production Checklist](#production-checklist)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start

1. **Clone and Configure**
```bash
git clone <repository-url>
cd fastapi-redis-celery-supabase
cp .env.example .env
# Edit .env with your configuration
```

2. **Start Services**
```bash
cd docker
docker-compose up -d
```

3. **Verify**
```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f api
docker-compose logs -f worker

# Health check
curl http://localhost:8000/api/v1/health
```

### Services

**API Service:**
- Port: 8000
- Replicas: 1 (scale with `docker-compose up --scale api=3`)
- Health check: `/api/v1/health`

**Worker Service:**
- Celery worker for background jobs
- Concurrency: 4
- Replicas: 1 (scale with `docker-compose up --scale worker=2`)

**Redis Service:**
- Port: 6379
- Persistence: Volume mounted at `/data`
- Health check: `redis-cli ping`

### Scaling

```bash
# Scale API instances
docker-compose up -d --scale api=3

# Scale workers
docker-compose up -d --scale worker=5
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f redis
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes 1.24+
- kubectl configured
- Helm 3.0+ (optional)

### Deployment Files

Create these Kubernetes manifests:

#### 1. Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fastapi-app
```

#### 2. ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
  namespace: fastapi-app
data:
  API_V1_PREFIX: "/api/v1"
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  CELERY_BROKER_URL: "redis://redis:6379/0"
  CELERY_RESULT_BACKEND: "redis://redis:6379/0"
```

#### 3. Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-secrets
  namespace: fastapi-app
type: Opaque
stringData:
  SUPABASE_URL: "https://your-project.supabase.co"
  SUPABASE_KEY: "your-supabase-key"
  JWT_SECRET: "your-jwt-secret"
```

#### 4. Redis Deployment
```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: fastapi-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: fastapi-app
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

#### 5. API Deployment
```yaml
# k8s/api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-api
  namespace: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-api
  template:
    metadata:
      labels:
        app: fastapi-api
    spec:
      containers:
      - name: api
        image: your-registry/fastapi-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fastapi-config
        - secretRef:
            name: fastapi-secrets
        livenessProbe:
          httpGet:
            path: /api/v1/health/liveness
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-api
  namespace: fastapi-app
spec:
  type: LoadBalancer
  selector:
    app: fastapi-api
  ports:
  - port: 80
    targetPort: 8000
```

#### 6. Worker Deployment
```yaml
# k8s/worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-worker
  namespace: fastapi-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-worker
  template:
    metadata:
      labels:
        app: fastapi-worker
    spec:
      containers:
      - name: worker
        image: your-registry/fastapi-worker:latest
        envFrom:
        - configMapRef:
            name: fastapi-config
        - secretRef:
            name: fastapi-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

#### 7. Horizontal Pod Autoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-api-hpa
  namespace: fastapi-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (edit first!)
kubectl apply -f k8s/secrets.yaml

# Create configmap
kubectl apply -f k8s/configmap.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Deploy API
kubectl apply -f k8s/api.yaml

# Deploy Worker
kubectl apply -f k8s/worker.yaml

# Deploy HPA
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get pods -n fastapi-app
kubectl get svc -n fastapi-app
```

### Access Application

```bash
# Get service IP
kubectl get svc fastapi-api -n fastapi-app

# Port forward (for testing)
kubectl port-forward -n fastapi-app svc/fastapi-api 8000:80

# Test
curl http://localhost:8000/api/v1/health
```

---

## Environment Configuration

### Required Variables

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
JWT_SECRET=your-secret-key-change-this-in-production
```

### Optional Variables

```bash
# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=FastAPI Boilerplate

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Cache
DEFAULT_CACHE_TTL=3600

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Production Checklist

### Security
- [ ] Change `JWT_SECRET` to cryptographically secure random string
- [ ] Use HTTPS only (configure reverse proxy/load balancer)
- [ ] Enable CORS with specific origins (not `*`)
- [ ] Review and adjust rate limiting settings
- [ ] Use environment-specific Supabase keys
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Set up firewall rules

### Performance
- [ ] Configure Redis max memory and eviction policy
- [ ] Set appropriate cache TTL values
- [ ] Configure Celery concurrency based on workload
- [ ] Enable Redis persistence (AOF or RDB)
- [ ] Set up connection pooling
- [ ] Configure worker autoscaling

### Monitoring
- [ ] Set up structured logging
- [ ] Configure log aggregation (ELK, Datadog, etc.)
- [ ] Set up APM (Application Performance Monitoring)
- [ ] Configure alerts for:
  - High error rate (> 1%)
  - Low cache hit rate (< 70%)
  - High response time (P99 > 1s)
  - Celery queue backup (> 1000 tasks)
- [ ] Set up uptime monitoring

### Reliability
- [ ] Configure health check endpoints
- [ ] Set up automated backups
- [ ] Test disaster recovery procedures
- [ ] Configure pod disruption budgets (Kubernetes)
- [ ] Set resource limits and requests
- [ ] Enable pod autoscaling

### Operations
- [ ] Document deployment procedures
- [ ] Set up CI/CD pipeline
- [ ] Configure automated testing
- [ ] Set up staging environment
- [ ] Document rollback procedures
- [ ] Set up database migrations workflow

---

## Monitoring

### Application Logs

```bash
# Docker
docker-compose logs -f api

# Kubernetes
kubectl logs -f -n fastapi-app deployment/fastapi-api
```

### Redis Monitoring

```bash
# Docker
docker-compose exec redis redis-cli INFO stats

# Kubernetes
kubectl exec -it -n fastapi-app deployment/redis -- redis-cli INFO stats
```

### Celery Monitoring

```bash
# Check active tasks
celery -A app.core.celery_app:celery_app inspect active

# Check registered tasks
celery -A app.core.celery_app:celery_app inspect registered

# Check stats
celery -A app.core.celery_app:celery_app inspect stats
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/v1/health

# Readiness
curl http://localhost:8000/api/v1/health/readiness

# Liveness
curl http://localhost:8000/api/v1/health/liveness
```

---

## Troubleshooting

### API Container Won't Start

**Symptoms:** Container exits immediately

**Solution:**
```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Missing environment variables
# 2. Redis not accessible
# 3. Invalid Supabase credentials

# Verify environment
docker-compose exec api env | grep SUPABASE
docker-compose exec api env | grep REDIS
```

### Redis Connection Failed

**Symptoms:** `Redis is not initialized` error

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping

# Check network
docker-compose exec api ping redis
```

### Celery Worker Not Processing Tasks

**Symptoms:** Tasks queued but not executed

**Solution:**
```bash
# Check worker logs
docker-compose logs worker

# Verify worker is registered
celery -A app.core.celery_app:celery_app inspect active

# Check Redis queue
docker-compose exec redis redis-cli LLEN celery

# Restart worker
docker-compose restart worker
```

### High Memory Usage

**Symptoms:** Container OOM killed

**Solution:**
```bash
# Check memory usage
docker stats

# Reduce Celery concurrency
# In docker-compose.yml:
command: celery -A app.core.celery_app worker --concurrency=2

# Increase container memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

### Slow Response Times

**Symptoms:** API responses > 500ms

**Solution:**
```bash
# Check cache hit rate
curl http://localhost:8000/api/v1/health

# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Check database query performance
# Enable query logging in Supabase dashboard

# Check Celery queue backup
celery -A app.core.celery_app inspect active
```

---

## CI/CD Example

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Build Docker images
        run: |
          docker build -f docker/Dockerfile.api -t myregistry/fastapi-api:latest .
          docker build -f docker/Dockerfile.worker -t myregistry/fastapi-worker:latest .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myregistry/fastapi-api:latest
          docker push myregistry/fastapi-worker:latest

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/fastapi-api fastapi-api=myregistry/fastapi-api:latest -n fastapi-app
          kubectl set image deployment/fastapi-worker fastapi-worker=myregistry/fastapi-worker:latest -n fastapi-app
```
