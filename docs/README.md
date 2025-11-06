# Documentation Index

FastAPI + Redis + Celery + Supabase Boilerplate için tüm dökümanlar.

---

## 📋 Genel Bakış

### [PRD.md](./PRD.md) - Product Requirements Document
**En önemli döküman** - Projenin tüm gereksinimlerini, hedeflerini ve spesifikasyonlarını içerir.

**İçerik:**
- Product overview ve hedefler
- Functional requirements (tüm API endpoints)
- Non-functional requirements (performance, security, etc.)
- Data models
- Background jobs
- Caching strategy
- Deployment requirements
- Success metrics

**Kimler Okumalı:**
- Tüm team members
- Yeni katılan developerlar
- Product managers
- Stakeholders

---

## 🏗️ Mimari & Tasarım

### [ARCHITECTURE.md](./ARCHITECTURE.md) - System Architecture
**Sistem mimarisi hakkında genel bilgi**

**İçerik:**
- System components (FastAPI, Redis, Celery, Supabase)
- Data flow
- Layer responsibilities
- Scalability considerations

**Ne Zaman Oku:**
- Projeye ilk başlarken
- Mimari kararlar alırken
- System design yaparken

---

### [CACHING.md](./CACHING.md) - Caching Strategy
**Cache stratejileri ve best practices**

**İçerik:**
- Cache patterns (Cache-Aside, Write-Through)
- Cache key design
- TTL guidelines
- Cache invalidation strategies
- Common pitfalls

**Ne Zaman Oku:**
- Cache implementasyonu eklerken
- Performance optimization yaparken
- Cache-related bug'ları çözerken

---

### [SCALING.md](./SCALING.md) - Scaling Guide
**Uygulama nasıl scale edilir**

**İçerik:**
- Current setup (Stage 2: 10K+ users)
- Metrics to monitor
- Horizontal scaling strategies
- When to scale to Stage 3
- Bottleneck identification

**Ne Zaman Oku:**
- Performance sorunları olduğunda
- Scale planning yaparken
- Production'a geçmeden önce

---

## 🔧 İmplementasyon

### [TASKS.md](./TASKS.md) - Background Tasks Guide
**Celery task geliştirme rehberi**

**İçerik:**
- Task types (immediate, scheduled, heavy processing)
- Task best practices (idempotency, retry, etc.)
- Creating new tasks
- Task patterns (email, data processing, cleanup)
- Monitoring tasks

**Ne Zaman Oku:**
- Background task yazarken
- Celery configuration yaparken
- Task debugging yaparken

---

### [API_REFERENCE.md](./API_REFERENCE.md) - API Reference
**Tüm API endpoints için detaylı referans**

**İçerik:**
- Authentication endpoints
- User management endpoints
- Content management endpoints
- Health check endpoints
- Error responses
- Rate limiting
- Client examples (Python, JavaScript, cURL)

**Ne Zaman Oku:**
- API kullanırken
- Frontend development yaparken
- Integration testing yaparken
- API documentation yazarken

---

### [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment Guide
**Production deployment rehberi**

**İçerik:**
- Docker deployment
- Kubernetes deployment
- Environment configuration
- Production checklist
- Monitoring setup
- Troubleshooting

**Ne Zaman Oku:**
- Production'a deploy ederken
- CI/CD pipeline kurarken
- Infrastructure setup yaparken
- Deployment sorunlarını çözerken

---

## 📚 Doküman Kullanım Rehberi

### Yeni Bir Feature Geliştirirken

1. **[PRD.md](./PRD.md)** - Feature requirements'ı kontrol et
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Hangi layer'da olacak?
3. **[CACHING.md](./CACHING.md)** - Cache gerekli mi?
4. **[TASKS.md](./TASKS.md)** - Background job gerekli mi?
5. **[API_REFERENCE.md](./API_REFERENCE.md)** - API design pattern'leri

### Bug Fix Yaparken

1. **İlgili dökümanı bul** (API issue ise API_REFERENCE.md)
2. **Expected behavior'u anla** (PRD.md)
3. **Architecture'ı kontrol et** (ARCHITECTURE.md)
4. **Monitoring** (SCALING.md - bottleneck identification)

### Production'a Geçerken

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment steps
2. **[SCALING.md](./SCALING.md)** - Performance metrics
3. **[PRD.md](./PRD.md)** - Production checklist

### Performance Sorunları

1. **[SCALING.md](./SCALING.md)** - Bottleneck identification
2. **[CACHING.md](./CACHING.md)** - Cache optimization
3. **[TASKS.md](./TASKS.md)** - Background job optimization

---

## 🎯 Hızlı Referans

| Soru | Doküman |
|------|---------|
| API endpoint'ler neler? | [API_REFERENCE.md](./API_REFERENCE.md) |
| Cache nasıl çalışıyor? | [CACHING.md](./CACHING.md) |
| Background task nasıl yazılır? | [TASKS.md](./TASKS.md) |
| Production'a nasıl deploy edilir? | [DEPLOYMENT.md](./DEPLOYMENT.md) |
| Nasıl scale edilir? | [SCALING.md](./SCALING.md) |
| System architecture nedir? | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Feature requirements nerede? | [PRD.md](./PRD.md) |

---

## 📝 Doküman Güncelleme

### Yeni Doküman Eklerken

1. Bu README'ye ekle
2. İlgili section'a yerleştir
3. "Ne Zaman Oku" kısmını ekle
4. Hızlı referans tablosunu güncelle

### Mevcut Doküman Güncellerken

1. Dokümanın başına "Last Updated" tarihini ekle
2. Changelog section ekle (major değişiklikler için)
3. İlgili diğer dökümanları da güncelle

---

## 🔗 Diğer Kaynaklar

### Kod Kuralları
Kod yazma kuralları ve best practices için: **`.cursor/rules/`** klasörü

- `01-architecture.mdc` - Katmanlı mimari
- `02-caching.mdc` - Cache implementation
- `03-background-tasks.mdc` - Task implementation
- `04-api-routes.mdc` - API development
- `05-testing.mdc` - Test yazma
- `06-code-style.mdc` - Code style

### External Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Redis Documentation](https://redis.io/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

## 💡 Öneriler

### İlk Defa Projeye Bakıyorsan

1. **[README.md](../README.md)** (Ana README) - Projeye genel bakış
2. **[PRD.md](./PRD.md)** - Ne yapıyor bu proje?
3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Nasıl çalışıyor?
4. **[API_REFERENCE.md](./API_REFERENCE.md)** - API'ler neler?

### Developer Onboarding

1. Tüm dökümanları sırayla oku
2. Local'de çalıştır ([DEPLOYMENT.md](./DEPLOYMENT.md))
3. Basit bir feature ekle (`.cursor/rules/` kurallarına göre)
4. Test yaz ([05-testing.mdc](../.cursor/rules/05-testing.mdc))

### Production'a Hazırlık

1. **[PRD.md](./PRD.md)** - Production checklist
2. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment guide
3. **[SCALING.md](./SCALING.md)** - Metrics & monitoring
4. **[API_REFERENCE.md](./API_REFERENCE.md)** - API test

---

**Not:** Tüm dökümanlar Markdown formatında ve kolayca okunabilir. Cursor IDE ile otomatik olarak görüntülenebilir.
