# Caching Strategy

## Cache Patterns

### 1. Cache-Aside (Lazy Loading)
- Check cache first
- On miss: query DB, cache result
- Used for: user data, posts

```python
# Example
cache_key = f"user:{user_id}"
cached_user = await cache.get(cache_key)
if cached_user:
    return cached_user

# Cache miss - query database
user = await db.get_user(user_id)
await cache.set(cache_key, user, ttl=3600)
return user
```

### 2. Write-Through
- Update DB and cache together
- Used for: user profile updates

```python
# Example
await db.update_user(user_id, data)
await cache.delete(f"user:{user_id}")
```

### 3. Cache Invalidation
- Delete on update/delete operations
- Pattern-based invalidation for related data

```python
# Example
await cache.invalidate_pattern("user:123:*")
```

## Cache Key Design

Format: `{entity}:{id}` or `{entity}:{id}:{field}`

### Examples
- `user:123` - User data
- `posts:page:1` - Posts list (page 1)
- `user:123:posts` - User's posts
- `post:456` - Individual post

## TTL Guidelines

| Entity Type | TTL | Reason |
|------------|-----|--------|
| User data | 1 hour | Rarely changes |
| Posts | 30 minutes | Moderately dynamic |
| Settings | 24 hours | Very static |
| List/pagination | 15 minutes | Frequently updated |

## Best Practices

### 1. Always Have DB Fallback
```python
try:
    cached_data = await cache.get(key)
    if cached_data:
        return cached_data
except Exception as e:
    logger.warning(f"Cache error: {e}")

# Fallback to database
return await db.get_data()
```

### 2. Don't Cache Sensitive Data
- Never cache passwords or tokens
- Be careful with personal information
- Consider encryption for sensitive cached data

### 3. Use Appropriate TTL
- Short TTL for frequently changing data
- Long TTL for static data
- Consider time-of-day patterns

### 4. Monitor Cache Hit Rate
- Target: >80% hit rate
- Low hit rate indicates:
  - TTL too short
  - Cache keys not matching
  - Data too volatile

## Cache Invalidation Strategies

### Immediate Invalidation
```python
# After update
await cache.delete(f"user:{user_id}")
```

### Pattern-Based Invalidation
```python
# Invalidate all related data
await cache.invalidate_pattern(f"user:{user_id}:*")
```

### Time-Based Expiration
```python
# Set TTL on creation
await cache.set(key, value, ttl=3600)
```

## Common Pitfalls

1. **Cache Stampede**: Multiple requests hitting DB when cache expires
   - Solution: Use locking or probabilistic early expiration

2. **Stale Data**: Cached data not matching DB
   - Solution: Proper invalidation strategy

3. **Memory Bloat**: Too much data in cache
   - Solution: Appropriate TTL and eviction policy

4. **Cache Inconsistency**: Different cache servers have different data
   - Solution: Use Redis cluster with proper replication

## Performance Tips

1. Use pipeline for multiple operations
2. Batch get/set operations when possible
3. Use appropriate serialization (JSON for flexibility)
4. Monitor Redis memory usage
5. Set max memory policy (e.g., allkeys-lru)
