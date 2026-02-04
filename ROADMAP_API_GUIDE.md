# 🗺️ Roadmap Generation API - دليل الاستخدام الكامل

## 📋 نظرة عامة

الـ endpoint الجديدة `/generate-roadmap/{user_id}` تُنشئ خطة تعليمية مخصصة (roadmap) لمدة 3-6 شهور بناءً على بيانات المستخدم الحالية.

---

## 🎯 الوظيفة الأساسية

### ماذا تفعل؟
1. ✅ تجلب بيانات المستخدم من قاعدة البيانات (ModelExtration)
2. ✅ تحلل مستوى المستخدم (Junior/Mid-level)
3. ✅ تُنشئ roadmap مخصصة باستخدام AI مجاني (Groq)
4. ✅ تُرجع خطة منظمة مع diagram

### المدخلات المطلوبة
- `user_id`: معرّف المستخدم (ApplicationUserId)

### الشروط
- المستخدم يجب أن يكون لديه بيانات في جدول `ModelExtrations`
- يعني لازم يكون رفع CV قبل كده باستخدام `/parse-cv`

---

## 🔧 طريقة الاستخدام

### 1️⃣ من cURL

```bash
curl -X POST "http://localhost:8000/generate-roadmap/0191a4b6-c4fc-752e-9d95-40b30fa7a9b6"
```

### 2️⃣ من JavaScript/TypeScript

```javascript
async function generateRoadmap(userId) {
  const response = await fetch(
    `http://localhost:8000/generate-roadmap/${userId}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const roadmap = await response.json();
  return roadmap;
}

// استخدام
try {
  const roadmap = await generateRoadmap('user-id-here');
  console.log('Roadmap Duration:', roadmap.roadmap_duration);
  console.log('Phases:', roadmap.roadmap.length);
  
  // عرض كل phase
  roadmap.roadmap.forEach(phase => {
    console.log(`\n${phase.phase}:`);
    console.log('Focus:', phase.focus);
    console.log('Topics:', phase.topics);
    console.log('Projects:', phase.projects);
  });
  
  // عرض Mermaid diagram
  console.log('\nMermaid Diagram:');
  console.log(roadmap.mermaid_code);
  
} catch (error) {
  console.error('Error:', error.message);
}
```

### 3️⃣ من C# (.NET)

```csharp
using System.Net.Http;
using System.Text.Json;

public class RoadmapService
{
    private readonly HttpClient _httpClient;
    
    public RoadmapService(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient();
    }
    
    public async Task<RoadmapResponse> GenerateRoadmapAsync(string userId)
    {
        var response = await _httpClient.PostAsync(
            $"http://localhost:8000/generate-roadmap/{userId}",
            null // No body needed
        );
        
        response.EnsureSuccessStatusCode();
        
        var json = await response.Content.ReadAsStringAsync();
        var roadmap = JsonSerializer.Deserialize<RoadmapResponse>(json);
        
        return roadmap;
    }
}

// Models
public class RoadmapResponse
{
    public string UserId { get; set; }
    public string RoadmapDuration { get; set; }
    public List<RoadmapPhase> Roadmap { get; set; }
    public string MermaidCode { get; set; }
}

public class RoadmapPhase
{
    public string Phase { get; set; }
    public List<string> Focus { get; set; }
    public List<string> Topics { get; set; }
    public List<string> Projects { get; set; }
}

// Usage in Controller
[HttpGet("my-roadmap")]
public async Task<IActionResult> GetMyRoadmap()
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    
    try
    {
        var roadmap = await _roadmapService.GenerateRoadmapAsync(userId);
        return Ok(roadmap);
    }
    catch (HttpRequestException ex)
    {
        if (ex.StatusCode == HttpStatusCode.NotFound)
        {
            return NotFound("Please upload your CV first");
        }
        return StatusCode(500, "Failed to generate roadmap");
    }
}
```

---

## 📤 شكل الـ Response

### مثال كامل:

```json
{
  "userId": "0191a4b6-c4fc-752e-9d95-40b30fa7a9b6",
  "roadmap_duration": "3-6 months",
  "roadmap": [
    {
      "phase": "Month 1",
      "focus": [
        "Strengthen C# and OOP fundamentals",
        "Deep dive into ASP.NET Core"
      ],
      "topics": [
        "Advanced C# features (delegates, events, LINQ)",
        "Dependency Injection in ASP.NET Core",
        "Middleware pipeline",
        "Configuration and Options pattern",
        "Logging with Serilog"
      ],
      "projects": [
        "Build a Task Management API with authentication (JWT)",
        "Implement logging and error handling middleware"
      ]
    },
    {
      "phase": "Month 2",
      "focus": [
        "Master Entity Framework Core",
        "Database design and optimization"
      ],
      "topics": [
        "EF Core migrations and relationships",
        "Query optimization and performance",
        "Repository pattern",
        "Unit of Work pattern",
        "Database indexing"
      ],
      "projects": [
        "Create a Blog API with EF Core (posts, comments, tags)",
        "Implement caching with Redis"
      ]
    },
    {
      "phase": "Month 3",
      "focus": [
        "Learn Clean Architecture",
        "Testing fundamentals"
      ],
      "topics": [
        "Clean Architecture layers",
        "CQRS pattern",
        "MediatR library",
        "Unit testing with xUnit",
        "Integration testing"
      ],
      "projects": [
        "Refactor previous projects to Clean Architecture",
        "Write unit and integration tests (70%+ coverage)"
      ]
    },
    {
      "phase": "Month 4",
      "focus": [
        "Docker and Containerization",
        "CI/CD basics"
      ],
      "topics": [
        "Docker basics and Dockerfile",
        "Docker Compose for multi-container apps",
        "GitHub Actions for CI/CD",
        "Deploying to Azure/AWS"
      ],
      "projects": [
        "Dockerize your API + SQL Server + Redis",
        "Setup CI/CD pipeline with GitHub Actions"
      ]
    },
    {
      "phase": "Month 5-6",
      "focus": [
        "Microservices architecture",
        "Cloud services (Azure/AWS)"
      ],
      "topics": [
        "Microservices communication (REST, gRPC, RabbitMQ)",
        "API Gateway pattern",
        "Azure App Service / AWS Lambda",
        "Monitoring and logging (Application Insights)",
        "Security best practices (OWASP)"
      ],
      "projects": [
        "Build a simple e-commerce system with 3 microservices:",
        "  - Product Service",
        "  - Order Service", 
        "  - Notification Service (RabbitMQ)",
        "Deploy to Azure with monitoring"
      ]
    }
  ],
  "mermaid_code": "graph TD\n    Start[Current Level: Junior Backend Developer] --> Month1[Month 1: ASP.NET Core Deep Dive]\n    Month1 --> Month2[Month 2: EF Core & Database Mastery]\n    Month2 --> Month3[Month 3: Clean Architecture & Testing]\n    Month3 --> Month4[Month 4: Docker & CI/CD]\n    Month4 --> Month5[Month 5-6: Microservices & Cloud]\n    Month5 --> End[Target: Mid-Level Backend Developer]\n    \n    Month1 -.-> P1[Project: Task Management API]\n    Month2 -.-> P2[Project: Blog API with Redis]\n    Month3 -.-> P3[Project: Clean Architecture Refactor]\n    Month4 -.-> P4[Project: Dockerized Full Stack]\n    Month5 -.-> P5[Project: E-commerce Microservices]"
}
```

---

## 🎨 عرض Mermaid Diagram

### في الـ Frontend:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
  <div id="roadmap-diagram"></div>
  
  <script>
    mermaid.initialize({ startOnLoad: true });
    
    async function displayRoadmap(userId) {
      const response = await fetch(`/generate-roadmap/${userId}`, {
        method: 'POST'
      });
      const data = await response.json();
      
      // إدراج الـ diagram
      document.getElementById('roadmap-diagram').innerHTML = 
        `<div class="mermaid">${data.mermaid_code}</div>`;
      
      // إعادة تفعيل Mermaid
      mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }
  </script>
</body>
</html>
```

### في React:

```jsx
import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';

function RoadmapViewer({ userId }) {
  const [roadmap, setRoadmap] = useState(null);
  
  useEffect(() => {
    mermaid.initialize({ startOnLoad: true });
    
    fetch(`/generate-roadmap/${userId}`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setRoadmap(data);
        
        // Render Mermaid
        setTimeout(() => {
          mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        }, 100);
      });
  }, [userId]);
  
  if (!roadmap) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Your Learning Roadmap</h1>
      <h2>{roadmap.roadmap_duration}</h2>
      
      {/* Mermaid Diagram */}
      <div className="mermaid">{roadmap.mermaid_code}</div>
      
      {/* Phases */}
      {roadmap.roadmap.map((phase, idx) => (
        <div key={idx} className="phase-card">
          <h3>{phase.phase}</h3>
          
          <div>
            <strong>Focus:</strong>
            <ul>
              {phase.focus.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
          
          <div>
            <strong>Topics:</strong>
            <ul>
              {phase.topics.map((t, i) => <li key={i}>{t}</li>)}
            </ul>
          </div>
          
          <div>
            <strong>Projects:</strong>
            <ul>
              {phase.projects.map((p, i) => <li key={i}>{p}</li>)}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## ⚠️ Error Handling

### 404 - User Not Found

```json
{
  "detail": "No data found for user: xyz. Please upload a CV first using /parse-cv endpoint."
}
```

**الحل:** المستخدم يحتاج رفع CV أولاً

```bash
# رفع CV
curl -X POST "http://localhost:8000/parse-cv?user_id=xyz" \
  -F "file=@cv.pdf"

# ثم إنشاء roadmap
curl -X POST "http://localhost:8000/generate-roadmap/xyz"
```

### 500 - AI Generation Error

```json
{
  "detail": "Failed to generate roadmap: LLM returned invalid JSON"
}
```

**الأسباب المحتملة:**
1. Groq API key غير صحيح
2. نفذ الـ rate limit
3. مشكلة في الاتصال بالإنترنت

**الحل:**
- تحقق من `GROQ_API_KEY` في `.env`
- انتظر دقيقة وأعد المحاولة

---

## 🤖 الموديل المستخدم

### الموديل الافتراضي: `llama-3.3-70b-versatile`

**المميزات:**
- ✅ مجاني 100% بدون بطاقة ائتمان
- ✅ سرعة عالية (Groq inference)
- ✅ جودة ممتازة في التحليل
- ✅ 12,000 tokens/minute (Free tier)

### تغيير الموديل

إذا أردت استخدام موديل آخر، عدّل في `.env`:

```env
# بدائل مجانية
GROQ_MODEL=llama-3.1-70b-versatile
# أو
GROQ_MODEL=mixtral-8x7b-32768
# أو
GROQ_MODEL=gemma2-9b-it
```

**ملاحظة:** كل الموديلات دي مجانية على Groq!

---

## 📊 مثال تفاعلي كامل

### Workflow كامل من البداية:

```bash
# 1. رفع CV
curl -X POST "http://localhost:8000/parse-cv?user_id=ahmed-123" \
  -F "file=@ahmed_cv.pdf"

# Response:
# {
#   "full_name": "Ahmed Sayed",
#   "skills": ["C#", "ASP.NET Core", ...],
#   ...
# }

# 2. إنشاء Roadmap
curl -X POST "http://localhost:8000/generate-roadmap/ahmed-123"

# Response: Complete roadmap JSON

# 3. عرض البيانات المحفوظة
curl "http://localhost:8000/model-extration/ahmed-123"

# 4. (اختياري) حذف البيانات
curl -X DELETE "http://localhost:8000/model-extration/ahmed-123"
```

---

## 🎯 Use Cases

### 1. Career Planning Dashboard
```javascript
// في dashboard المستخدم
const roadmap = await generateRoadmap(currentUser.id);
displayRoadmapTimeline(roadmap);
trackProgress(roadmap.roadmap);
```

### 2. Onboarding New Users
```javascript
// بعد رفع CV مباشرة
await uploadCV(cvFile, userId);
const roadmap = await generateRoadmap(userId);
showWelcomeRoadmap(roadmap);
```

### 3. Skill Gap Analysis
```javascript
// مقارنة مع job requirements
const roadmap = await generateRoadmap(userId);
const jobRequirements = await fetchJobRequirements(jobId);
const gaps = analyzeGaps(roadmap, jobRequirements);
```

---

## 🔐 Security Considerations

### ✅ Best Practices:

1. **التحقق من الهوية:**
```csharp
// في .NET Controller
[Authorize]
[HttpPost("generate-roadmap")]
public async Task<IActionResult> GenerateRoadmap()
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    // استخدم userId من المصادقة، مش من request
    var roadmap = await _roadmapService.GenerateRoadmapAsync(userId);
    return Ok(roadmap);
}
```

2. **Rate Limiting:**
```python
# في FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post(
    "/generate-roadmap/{user_id}",
    dependencies=[Depends(RateLimiter(times=5, hours=1))]
)
async def generate_roadmap_endpoint(user_id: str):
    # ...
```

3. **Caching:**
```python
# Cache roadmaps لنفس اليوزر لمدة 24 ساعة
from functools import lru_cache
import hashlib
import json

def cache_key(user_data: dict) -> str:
    return hashlib.md5(json.dumps(user_data, sort_keys=True).encode()).hexdigest()

# استخدم Redis للـ production
```

---

## 📈 Performance Tips

### 1. Database Queries
```sql
-- تأكد من وجود index
CREATE INDEX IX_ModelExtrations_UserId 
ON ModelExtrations(ApplicationUserId);
```

### 2. Response Time
- متوسط الوقت: 5-10 ثواني
- يعتمد على:
  - سرعة Groq API (عادة سريع جداً)
  - حجم البيانات
  - سرعة الاتصال

### 3. Optimization
```python
# استخدم async/await بشكل صحيح
# الـ code الحالي محسّن بالفعل
```

---

## 🆘 Troubleshooting

### المشكلة: "Mermaid diagram لا يظهر"

**الحل:**
```html
<!-- تأكد من تحميل Mermaid library -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>

<script>
  mermaid.initialize({ 
    startOnLoad: true,
    theme: 'default'
  });
</script>
```

### المشكلة: "Roadmap غير دقيقة"

**الحل:**
1. تأكد من بيانات المستخدم كاملة ودقيقة
2. جرّب موديل أقوى: `llama-3.3-70b-versatile`
3. عدّل الـ prompt في `roadmap_service.py`

### المشكلة: "GROQ_API_KEY not set"

**الحل:**
```bash
# في .env
GROQ_API_KEY=gsk_your_key_here

# احصل على key من:
https://console.groq.com/keys
```

---

## 🎓 التكامل الكامل

### Full Stack Example (React + .NET + Python):

**Frontend (React):**
```jsx
const handleGenerateRoadmap = async () => {
  setLoading(true);
  try {
    // استدعي .NET API
    const response = await fetch('/api/roadmap/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const roadmap = await response.json();
    setRoadmap(roadmap);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};
```

**Backend (.NET):**
```csharp
[Authorize]
[HttpPost("generate")]
public async Task<IActionResult> GenerateRoadmap()
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    
    // استدعي Python API
    var response = await _httpClient.PostAsync(
        $"http://python-api:8000/generate-roadmap/{userId}",
        null
    );
    
    var roadmap = await response.Content.ReadFromJsonAsync<RoadmapResponse>();
    
    // (اختياري) احفظ في database
    await _context.Roadmaps.AddAsync(new Roadmap {
        UserId = userId,
        Data = JsonSerializer.Serialize(roadmap),
        CreatedAt = DateTime.UtcNow
    });
    await _context.SaveChangesAsync();
    
    return Ok(roadmap);
}
```

---

## ✨ الخلاصة

### ما تم إضافته:

1. ✅ **Schema جديد:** `roadmap_schema.py`
2. ✅ **Service جديد:** `roadmap_service.py`
3. ✅ **Endpoint جديد:** `POST /generate-roadmap/{user_id}`
4. ✅ **AI Integration:** باستخدام Groq (مجاني)
5. ✅ **Mermaid Support:** لعرض visual roadmap

### الاستخدام:
```bash
# خطوة واحدة فقط!
curl -X POST "http://localhost:8000/generate-roadmap/USER_ID"
```

### النتيجة:
- 🎯 Roadmap مخصصة 3-6 شهور
- 📊 Mermaid diagram جاهز للعرض
- 🚀 مهارات محددة ومشاريع عملية
- 💯 بدون تكاليف (Free AI)

---

**Built with ❤️ for Career Path**
