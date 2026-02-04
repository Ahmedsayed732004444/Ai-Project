# 🚀 دليل البداية السريعة - Career Path CV Parser

## خطوات التشغيل في 5 دقائق

### 1️⃣ التثبيت الأساسي

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt
```

### 2️⃣ إعداد ملف .env

```bash
cp .env.example .env
```

**عدّل الملف وأضف Groq API Key فقط:**
```env
GROQ_API_KEY=gsk_your_key_here
```

احصل على المفتاح مجاناً من: https://console.groq.com

### 3️⃣ اختبار الاتصال

```bash
python test_database.py
```

يجب أن ترى:
```
✅ SUCCESS - Connected to Career_Path database
✅ SUCCESS - ModelExtration created
...
```

### 4️⃣ تشغيل الخادم

```bash
uvicorn app.main:app --reload
```

### 5️⃣ اختبار API

افتح المتصفح:
- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **DB Health:** http://localhost:8000/db-health

---

## 📝 أمثلة الاستخدام

### مثال 1: تحليل CV فقط (بدون حفظ)

```bash
curl -X POST "http://localhost:8000/parse-cv" \
  -F "file=@my_cv.pdf"
```

### مثال 2: تحليل وحفظ في قاعدة البيانات

```bash
curl -X POST "http://localhost:8000/parse-cv?user_id=USER_ID" \
  -F "file=@my_cv.pdf"
```

**ملحوظة:** `user_id` يجب أن يكون `ApplicationUserId` موجود في `AspNetUsers`

### مثال 3: استرجاع البيانات

```bash
curl http://localhost:8000/model-extration/USER_ID
```

---

## 🔧 التكامل مع .NET

### من C# Controller:

```csharp
using System.Net.Http;
using System.Net.Http.Headers;

public class CVController : ControllerBase
{
    private readonly HttpClient _httpClient;
    
    public CVController(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient();
    }
    
    [HttpPost("upload-cv")]
    public async Task<IActionResult> UploadCV(IFormFile file)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        
        using var content = new MultipartFormDataContent();
        using var fileContent = new StreamContent(file.OpenReadStream());
        fileContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType);
        content.Add(fileContent, "file", file.FileName);
        
        var response = await _httpClient.PostAsync(
            $"http://localhost:8000/parse-cv?user_id={userId}",
            content
        );
        
        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadAsStringAsync();
            return Ok(new { message = "CV processed successfully", data = result });
        }
        
        return BadRequest("CV processing failed");
    }
    
    [HttpGet("my-cv-data")]
    public async Task<IActionResult> GetMyCVData()
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        
        var response = await _httpClient.GetAsync(
            $"http://localhost:8000/model-extration/{userId}"
        );
        
        if (response.IsSuccessStatusCode)
        {
            var data = await response.Content.ReadAsStringAsync();
            return Ok(data);
        }
        
        return NotFound("No CV data found");
    }
}
```

### تسجيل HttpClient في Program.cs:

```csharp
builder.Services.AddHttpClient();
```

---

## 🗄️ البيانات المحفوظة

عند رفع CV، يتم حفظ:

### في جدول `ModelExtrations`:
- FullName
- Email  
- Phone
- Location
- Summary
- Skills (JSON array)
- Certifications (JSON array)
- Languages (JSON array)

### في جدول `Education`:
- Degree
- Field
- Institution
- Year

### في جدول `Experience`:
- JobTitle
- Company
- StartDate
- EndDate
- Description

---

## ⚠️ ملاحظات مهمة

1. **ApplicationUserId:**
   - يجب أن يكون موجوداً في `AspNetUsers`
   - علاقة One-to-One (مستخدم واحد = ModelExtration واحد)
   - رفع CV جديد = تحديث البيانات القديمة

2. **Groq API:**
   - مجاني لكن لديه حد استخدام يومي
   - إذا نفد الحد، سيفشل التحليل
   - احصل على API key من: https://console.groq.com

3. **ODBC Driver:**
   - **ضروري جداً** للاتصال بـ SQL Server
   - يجب تثبيته قبل تشغيل المشروع
   - راجع README لتعليمات التثبيت

4. **الملفات المدعومة:**
   - PDF (نص فقط، ليس صور)
   - DOCX
   - حجم أقصى: 10 MB

---

## 🐛 حل المشاكل الشائعة

### المشكلة: "GROQ_API_KEY is not set"
```bash
# الحل: أضف المفتاح في .env
echo "GROQ_API_KEY=gsk_your_key" >> .env
```

### المشكلة: "Database connection failed"
```bash
# الحل: تحقق من ODBC Driver
odbcinst -j

# تثبيت ODBC Driver (Ubuntu)
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### المشكلة: "User not found"
```bash
# الحل: تأكد أن user_id موجود في AspNetUsers
# استخدم user_id من جدول AspNetUsers
```

### المشكلة: "No text extracted"
```bash
# الحل: الملف قد يكون:
# - PDF مصور (يحتاج OCR)
# - محمي بكلمة مرور
# - تالف
```

---

## 📊 مثال كامل

```bash
# 1. تشغيل الخادم
uvicorn app.main:app --reload

# 2. في terminal آخر، اختبر:
curl -X POST "http://localhost:8000/parse-cv?user_id=0191a4b6-c4fc-752e-9d95-40b30fa7a9b6" \
  -F "file=@ahmed_cv.pdf"

# 3. تحقق من الحفظ:
curl http://localhost:8000/model-extration/0191a4b6-c4fc-752e-9d95-40b30fa7a9b6

# 4. أو من SQL Server Management Studio:
SELECT * FROM ModelExtrations WHERE ApplicationUserId = '0191a4b6-c4fc-752e-9d95-40b30fa7a9b6'
SELECT * FROM Education
SELECT * FROM Experience
```

---

## 🎯 الخطوات التالية

1. ✅ شغّل `test_database.py` للتأكد من كل شيء
2. ✅ جرّب رفع CV من Swagger UI
3. ✅ تحقق من البيانات في SQL Server
4. ✅ ادمج مع .NET Backend بتاعك
5. ✅ اعمل Frontend لرفع CVs

---

**Good Luck! 🚀**

إذا واجهت أي مشكلة، راجع `README.md` الكامل أو افتح Issue.
