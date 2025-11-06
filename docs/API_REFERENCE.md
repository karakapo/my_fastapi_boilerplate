# API Reference

**Base URL:** `http://localhost:8000/api/v1`

**Version:** 1.0

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```http
Authorization: Bearer {access_token}
```

---

## Authentication Endpoints

### POST /auth/signup

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "message": "User registered successfully. Please check your email for verification."
  }
}
```

**Errors:**
- `400` - Invalid input
- `409` - Email already exists

---

### POST /auth/login

Authenticate user and get access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com"
    }
  }
}
```

**Errors:**
- `401` - Invalid credentials

---

### POST /auth/logout

Logout current user.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

### POST /auth/refresh

Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Errors:**
- `401` - Invalid refresh token

---

## User Endpoints

### GET /users/me

Get current authenticated user's profile.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "email_confirmed_at": "2024-01-01T00:00:00Z"
  }
}
```

**Caching:** 1 hour TTL

**Errors:**
- `401` - Unauthorized

---

### GET /users/{user_id}

Get user by ID.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Parameters:**
- `user_id` (path) - User ID

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Caching:** 1 hour TTL

**Errors:**
- `401` - Unauthorized
- `404` - User not found

---

### PUT /users/{user_id}

Update user profile.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Parameters:**
- `user_id` (path) - User ID

**Request:**
```json
{
  "email": "newemail@example.com"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "newemail@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "message": "User updated successfully"
  }
}
```

**Errors:**
- `401` - Unauthorized
- `403` - Forbidden (can only update own profile)
- `404` - User not found
- `422` - Validation error

---

## Post Endpoints

### GET /posts

List posts with pagination.

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 20, max: 100) - Items per page
- `published_only` (boolean, default: true) - Filter published posts only

**Example:**
```http
GET /api/v1/posts?page=1&page_size=20&published_only=true
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "post-1",
      "title": "Post 1",
      "content": "Content for post 1",
      "published": true,
      "author_id": "user-1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 100,
  "has_next": true
}
```

**Caching:** 30 minutes TTL

---

### POST /posts

Create a new post.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "title": "My New Post",
  "content": "This is the post content",
  "published": true
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "post": {
      "id": "new-post-id",
      "title": "My New Post",
      "content": "This is the post content",
      "published": true,
      "author_id": "user-id",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "message": "Post created successfully"
  }
}
```

**Side Effects:**
- Cache invalidated for post lists
- Notification email sent (background) if published

**Errors:**
- `401` - Unauthorized
- `422` - Validation error

---

### GET /posts/{post_id}

Get post by ID.

**Parameters:**
- `post_id` (path) - Post ID

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "post-123",
    "title": "Post Title",
    "content": "Post content",
    "published": true,
    "author_id": "user-1",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Caching:** 30 minutes TTL

**Errors:**
- `404` - Post not found

---

### DELETE /posts/{post_id}

Delete post by ID.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Parameters:**
- `post_id` (path) - Post ID

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "Post deleted successfully"
  }
}
```

**Side Effects:**
- Cache invalidated for post and post lists

**Errors:**
- `401` - Unauthorized
- `403` - Forbidden (not post owner)
- `404` - Post not found

---

## Health Endpoints

### GET /health

Check system health status.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "redis": {
        "status": "healthy",
        "message": "Connected"
      },
      "supabase": {
        "status": "healthy",
        "message": "Connected"
      }
    }
  }
}
```

**Status Values:**
- `healthy` - All services operational
- `degraded` - Some services unavailable

**No Authentication Required**
**No Caching**

---

### GET /health/readiness

Readiness check for Kubernetes.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "ready",
    "message": "Service is ready to accept traffic"
  }
}
```

---

### GET /health/liveness

Liveness check for Kubernetes.

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "alive",
    "message": "Service is alive"
  }
}
```

---

## Error Responses

All endpoints may return these common error responses:

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid request",
    "details": {}
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": {}
  }
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource",
    "details": {}
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": {
      "user_id": "123"
    }
  }
}
```

### 422 Validation Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "type": "value_error.email"
      }
    ]
  }
}
```

### 429 Rate Limit Exceeded
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 60 seconds",
    "details": {
      "retry_after": 60
    }
  }
}
```

**Headers:**
```http
Retry-After: 60
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": {}
  }
}
```

---

## Rate Limiting

All endpoints are rate-limited per IP address:
- **Limit:** 100 requests per minute
- **Window:** Sliding window (60 seconds)
- **Response:** `429 Too Many Requests`

**Response Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067260
```

---

## Pagination

List endpoints support pagination with these parameters:

- `page` (integer, min: 1, default: 1)
- `page_size` (integer, min: 1, max: 100, default: 20)

**Response Format:**
```json
{
  "success": true,
  "data": [...],
  "page": 1,
  "page_size": 20,
  "total": 100,
  "has_next": true
}
```

---

## OpenAPI Documentation

Interactive API documentation available at:

- **Swagger UI:** `http://localhost:8000/api/v1/docs`
- **ReDoc:** `http://localhost:8000/api/v1/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/v1/openapi.json`

---

## Client Examples

### Python (httpx)
```python
import httpx

# Login
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
data = response.json()
access_token = data["data"]["access_token"]

# Authenticated request
response = httpx.get(
    "http://localhost:8000/api/v1/users/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
user = response.json()
```

### JavaScript (fetch)
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});
const {data} = await loginResponse.json();
const accessToken = data.access_token;

// Authenticated request
const userResponse = await fetch('http://localhost:8000/api/v1/users/me', {
  headers: {'Authorization': `Bearer ${accessToken}`}
});
const user = await userResponse.json();
```

### cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Authenticated request
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer {access_token}"
```
