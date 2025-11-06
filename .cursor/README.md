# Cursor Rules - FastAPI Boilerplate

Bu klasör, FastAPI boilerplate projesi için detaylı coding kuralları ve best practice'leri içerir.

## Dosyalar

### 01-architecture.mdc
- Katmanlı mimari prensipler
- Dosya organizasyonu
- Dependency injection
- Data flow patterns
- Service layer tasarımı

**Ne Zaman Kullan:**
- Yeni feature eklerken
- Kod yapısı hakkında karar verirken
- Servis/route organizasyonu için

---

### 02-caching.mdc
- Cache patterns (Cache-Aside, Write-Through)
- Cache key naming conventions
- TTL kuralları
- Cache invalidation stratejileri
- Performance optimization

**Ne Zaman Kullan:**
- Cache implementasyonu eklerken
- Performance sorunları için
- Cache stratejisi belirlerken

---

### 03-background-tasks.mdc
- Celery task yazma kuralları
- İdempotent task tasarımı
- Retry logic
- Timeout configuration
- Task monitoring

**Ne Zaman Kullan:**
- Background job eklerken
- Email/notification gönderirken
- Heavy computation için

---

### 04-api-routes.mdc
- REST API endpoint yazma
- HTTP methods & status codes
- Request/response validation
- Query parameters
- Authentication/authorization
- Error handling

**Ne Zaman Kullan:**
- Yeni API endpoint eklerken
- Route refactor ederken
- API tasarımı için

---

### 05-testing.mdc
- Unit test yazma
- Integration test
- Fixtures & mocking
- Test best practices
- CI/CD integration

**Ne Zaman Kullan:**
- Test yazarken
- Test stratejisi belirlerken
- Coverage artırmak için

---

### 06-code-style.mdc
- Type hints
- Async/await patterns
- Logging
- Naming conventions
- Documentation
- Performance tips

**Ne Zaman Kullan:**
- Her zaman! (code style guide)
- Code review yaparken
- Refactoring yaparken

---

## Hızlı Başvuru

### Yeni Feature Eklerken
1. `01-architecture.mdc` - Hangi katmanda olacak?
2. `02-caching.mdc` - Cache gerekli mi?
3. `03-background-tasks.mdc` - Background job gerekli mi?
4. `04-api-routes.mdc` - API endpoint tasarımı
5. `05-testing.mdc` - Test yaz
6. `06-code-style.mdc` - Code style check

### Cache Eklerken
1. `02-caching.mdc` - Cache pattern seç
2. `02-caching.mdc` - Cache key format
3. `02-caching.mdc` - TTL belirle
4. `06-code-style.mdc` - Code style

### Background Task Eklerken
1. `03-background-tasks.mdc` - Task pattern seç
2. `03-background-tasks.mdc` - İdempotent yap
3. `03-background-tasks.mdc` - Retry logic ekle
4. `05-testing.mdc` - Test yaz

### API Endpoint Eklerken
1. `04-api-routes.mdc` - HTTP method & status code
2. `04-api-routes.mdc` - Request/response models
3. `01-architecture.mdc` - Service layer kullan
4. `05-testing.mdc` - Integration test yaz

---

## Cursor IDE'de Kullanım

Cursor IDE bu dosyaları otomatik okur ve öneriler sunar.

### Örnek Prompt'lar:

```
"Yeni bir user endpoint ekle, caching kullan"
→ Cursor: 01-architecture.mdc ve 02-caching.mdc'yi okuyarak uygun kod üretir

"Email gönderen background task yaz"
→ Cursor: 03-background-tasks.mdc'ye göre idempotent task oluşturur

"Bu endpoint için test yaz"
→ Cursor: 05-testing.mdc'deki pattern'leri kullanır
```

---

## Önemli Prensipler

### 1. Katmanlı Mimari
```
Route → Service → Database/Cache
```

### 2. Her Zaman Cache Kullan (Gerekirse)
```python
async def get_user(user_id: str):
    # 1. Cache check
    # 2. DB query
    # 3. Cache result
```

### 3. Heavy Operations = Background Task
```python
# ❌ YANLIŞ
@router.post("/process")
async def process(data):
    result = heavy_computation(data)  # Blocks!

# ✅ DOĞRU
@router.post("/process")
async def process(data):
    task = heavy_computation.delay(data)
    return {"task_id": task.id}
```

### 4. Type Hints Her Yerde
```python
async def get_user(user_id: str) -> UserResponse:
    pass
```

### 5. Test Yaz
```python
@pytest.mark.asyncio
async def test_get_user():
    # Arrange, Act, Assert
    pass
```

---

## Güncelleme

Bu dosyaları projenin ihtiyaçlarına göre güncelleyin:

1. Yeni pattern ekle
2. Örnekleri güncelle
3. Best practice'leri ekle
4. Anti-pattern'leri dokümante et

---

## Katkıda Bulunma

Yeni pattern veya best practice bulduğunuzda:
1. İlgili dosyayı bulun
2. Örnek ekleyin (✅ DOĞRU ve ❌ YANLIŞ)
3. Açıklama yazın
