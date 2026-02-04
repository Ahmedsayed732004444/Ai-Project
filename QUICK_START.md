# 🚀 Quick Start - Roadmap Feature

## تشغيل سريع في 3 خطوات

### 1️⃣ نسخ الملفات الجديدة

```bash
# نسخ الملفات الجديدة إلى مشروعك
cp app/schemas/roadmap_schema.py your-project/app/schemas/
cp app/services/roadmap_service.py your-project/app/services/
cp app/api/routes.py your-project/app/api/
```

### 2️⃣ تشغيل الخادم

```bash
cd your-project
uvicorn app.main:app --reload
```

### 3️⃣ اختبار الـ Endpoint

```bash
# اختبار 1: رفع CV
curl -X POST "http://localhost:8000/parse-cv?user_id=test-123" \
  -F "file=@cv.pdf"

# اختبار 2: إنشاء Roadmap
curl -X POST "http://localhost:8000/generate-roadmap/test-123"
```

---

## ✅ التحقق من النجاح

يجب أن ترى response مثل:

```json
{
  "userId": "test-123",
  "roadmap_duration": "3-6 months",
  "roadmap": [
    {
      "phase": "Month 1",
      "focus": ["ASP.NET Core", "EF Core"],
      "topics": [...],
      "projects": [...]
    }
  ],
  "mermaid_code": "graph TD\n..."
}
```

---

## 🧪 اختبار شامل

```bash
python test_roadmap.py
```

يجب أن ترى:
```
✅ SUCCESS - Roadmap generated!
✅ ALL TESTS PASSED!
```

---

## 📚 التوثيق الكامل

اقرأ:
- **ROADMAP_API_GUIDE.md** - شرح تفصيلي
- **NEW_FEATURES.md** - نظرة عامة على الميزات

---

## ⚡ Integration Example

### React

```jsx
const RoadmapButton = ({ userId }) => {
  const [roadmap, setRoadmap] = useState(null);
  
  const generate = async () => {
    const res = await fetch(`/api/roadmap/${userId}`, {
      method: 'POST'
    });
    setRoadmap(await res.json());
  };
  
  return (
    <>
      <button onClick={generate}>Generate Roadmap</button>
      {roadmap && <RoadmapView data={roadmap} />}
    </>
  );
};
```

### .NET

```csharp
[HttpPost("my-roadmap")]
public async Task<IActionResult> GenerateRoadmap()
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    var response = await _httpClient.PostAsync(
        $"http://localhost:8000/generate-roadmap/{userId}",
        null
    );
    return Ok(await response.Content.ReadFromJsonAsync<Roadmap>());
}
```

---

## 🎉 الخلاصة

### ما تم إضافته:
- ✅ 3 ملفات فقط (schemas, service, routes)
- ✅ Endpoint واحدة جديدة
- ✅ بدون dependencies جديدة
- ✅ مجاني 100%

### الاستخدام:
```bash
POST /generate-roadmap/{user_id}
```

**Done! 🚀**
