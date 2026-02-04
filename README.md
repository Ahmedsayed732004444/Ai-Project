# Career Path - CV Parser API 🚀

**خدمة Python AI لتحليل السيرة الذاتية ودمجها مع قاعدة بيانات Career Path (.NET)**

هذا المشروع يوفر API لتحليل ملفات الـ CV (PDF/DOCX) باستخدام الذكاء الاصطناعي وحفظ البيانات المستخرجة مباشرة في جدول **ModelExtrations** في قاعدة بيانات Career Path الموجودة.

---

## ✨ المميزات

- ✅ تحليل ملفات CV (PDF و DOCX) بالذكاء الاصطناعي
- ✅ استخراج بيانات منظمة (Personal Info, Skills, Education, Experience)
- ✅ حفظ مباشر في جدول `ModelExtrations` بقاعدة البيانات
- ✅ دعم كامل لـ `Education` و `Experience` كـ Owned Collections
- ✅ API موثق بالكامل (Swagger UI)
- ✅ دعم CORS للتكامل مع Frontend
- ✅ متوافق 100% مع Entity Framework Models

---

## 🗄️ البنية المستخدمة

المشروع يتعامل مع الجداول التالية من Career_Path database:

### ModelExtrations (الجدول الرئيسي)
```csharp
public class ModelExtration
{
    public int Id { get; set; }
    public string ApplicationUserId { get; set; }
    public string FullName { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public string Location { get; set; }
    public string Summary { get; set; }
    public List<string> Skills { get; set; }
    public List<Education> Education { get; set; }
    public List<Experience> Experience { get; set; }
    public List<string> Certifications { get; set; }
    public List<string> Languages { get; set; }
}
```

### Education (Owned Collection)
```csharp
[Owned]
public class Education
{
    public string Degree { get; set; }
    public string Field { get; set; }
    public string Institution { get; set; }
    public string Year { get; set; }
}
```

### Experience (Owned Collection)
```csharp
[Owned]
public class Experience
{
    public string JobTitle { get; set; }
    public string Company { get; set; }
    public string StartDate { get; set; }
    public string EndDate { get; set; }
    public string Description { get; set; }
}
```

---

## 📋 المتطلبات

- Python 3.11+
- SQL Server Database (Career_Path)
- ODBC Driver 17 for SQL Server
- Groq API Key (مجاني من https://console.groq.com)

---

## 🛠️ التثبيت

### 1. تثبيت ODBC Driver

#### Windows:
```bash
# حمّل من:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

#### Linux (Ubuntu/Debian):
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
apt-get install -y unixodbc-dev
```

#### macOS:
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17
```

### 2. تثبيت المشروع

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt
```

### 3. إعداد ملف .env

```bash
cp .env.example .env
```

ثم عدّل الملف وأضف Groq API Key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

بيانات قاعدة البيانات موجودة مسبقاً:
```env
DB_SERVER=db38948.public.databaseasp.net
DB_NAME=db38948
DB_USER=db38948
DB_PASSWORD=M?i98zJ=T!d4
```

---

## 🚀 التشغيل

### محلياً:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker:
```bash
# بناء
docker build -t cv-parser .

# تشغيل
docker run -p 8000:8000 --env-file .env cv-parser
```

---

## 📚 استخدام API

### 1. فحص الصحة

```bash
# فحص API
curl http://localhost:8000/health

# فحص قاعدة البيانات
curl http://localhost:8000/db-health
```

### 2. تحليل CV (بدون حفظ)

```bash
curl -X POST "http://localhost:8000/parse-cv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@my_cv.pdf"
```

الرد:
```json
{
  "full_name": "Ahmed Sayed",
  "email": "ahmed@example.com",
  "phone": "+20123456789",
  "location": "Cairo, Egypt",
  "summary": "Software Developer with 5 years experience...",
  "skills": ["Python", "C#", ".NET", "SQL Server"],
  "education": [
    {
      "degree": "Bachelor",
      "field": "Computer Science",
      "institution": "Cairo University",
      "year": "2020"
    }
  ],
  "experience": [
    {
      "job_title": "Backend Developer",
      "company": "Tech Corp",
      "start_date": "Jan 2020",
      "end_date": "Present",
      "description": "Developed APIs using .NET..."
    }
  ],
  "certifications": ["AWS Certified"],
  "languages": ["Arabic (Native)", "English (Fluent)"]
}
```

### 3. تحليل CV وحفظه في قاعدة البيانات

```bash
curl -X POST "http://localhost:8000/parse-cv?user_id=USER_ID_HERE" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@my_cv.pdf"
```

**ملحوظة:** `user_id` يجب أن يكون `ApplicationUserId` موجود في جدول `AspNetUsers`

### 4. استرجاع ModelExtration لمستخدم معين

```bash
curl http://localhost:8000/model-extration/USER_ID_HERE
```

### 5. حذف ModelExtration

```bash
curl -X DELETE http://localhost:8000/model-extration/USER_ID_HERE
```

---

## 📖 توثيق API

بعد تشغيل المشروع، افتح:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔧 التكامل مع .NET Backend

### من C# Controller:

```csharp
// رفع CV عبر Python API
var client = new HttpClient();
var content = new MultipartFormDataContent();
content.Add(new StreamContent(cvFileStream), "file", "cv.pdf");

var response = await client.PostAsync(
    $"http://localhost:8000/parse-cv?user_id={userId}",
    content
);

if (response.IsSuccessStatusCode)
{
    // تم الحفظ في ModelExtrations تلقائياً
    var data = await response.Content.ReadAsStringAsync();
}
```

### استرجاع البيانات:

```csharp
// من Python API
var response = await client.GetAsync(
    $"http://localhost:8000/model-extration/{userId}"
);

// أو من EF Core مباشرة
var modelExtration = await _context.ModelExtrations
    .Include(m => m.Education)
    .Include(m => m.Experience)
    .FirstOrDefaultAsync(m => m.ApplicationUserId == userId);
```

---

## 🔍 آلية العمل

1. **رفع ملف CV** → API تستقبل PDF/DOCX
2. **استخراج النص** → pdfplumber أو python-docx
3. **تحليل AI** → Groq LLM يستخرج البيانات المنظمة
4. **التحقق** → Pydantic يتحقق من صحة البيانات
5. **الحفظ** → مباشرة في جدول `ModelExtrations`
   - Education تُحفظ في جدول `Education` (Owned)
   - Experience تُحفظ في جدول `Experience` (Owned)
   - Skills, Certifications, Languages تُحفظ كـ JSON arrays

---

## ⚙️ ملاحظات تقنية

### معالجة Skills و Certifications و Languages

هذه الحقول محفوظة كـ **JSON arrays** في SQL Server:
- في .NET: `List<string>`
- في Python: `list[str]`
- في SQL: `nvarchar(max)` يحتوي على `["item1", "item2"]`

### Owned Collections (Education & Experience)

- EF Core يحفظها في جداول منفصلة مع `ModelExtrationId`
- Python API تتعامل معها بنفس الطريقة
- Cascade Delete مفعّل (حذف ModelExtration يحذف Education و Experience)

### ApplicationUserId

- يجب أن يكون موجوداً في جدول `AspNetUsers`
- العلاقة: One-to-One بين `ApplicationUser` و `ModelExtration`
- إذا كان المستخدم لديه ModelExtration موجود، سيتم **التحديث** بدلاً من الإضافة

---

## 🐛 استكشاف الأخطاء

### خطأ: "GROQ_API_KEY is not set"
**الحل:** أضف المفتاح في `.env`

### خطأ: "Database connection failed"
**الحل:** 
1. تحقق من تثبيت ODBC Driver
2. تحقق من بيانات الاتصال في `.env`
3. جرّب: `curl http://localhost:8000/db-health`

### خطأ: "No text extracted"
**الحل:** الملف قد يكون:
- صور فقط (بدون نص)
- محمي بكلمة مرور
- تالف

### خطأ: "User not found"
**الحل:** تأكد أن `ApplicationUserId` موجود في `AspNetUsers`

---

## 📊 أمثلة استخدام

### سيناريو 1: تسجيل مستخدم جديد

```python
# 1. المستخدم يرفع CV
# 2. تحليل CV
# 3. حفظ في ModelExtrations
# 4. استخدام البيانات لملء UserProfile تلقائياً
```

### سيناريو 2: تحديث ملف شخصي

```python
# 1. المستخدم يرفع CV جديد
# 2. تحليل CV
# 3. تحديث ModelExtration الموجود
# 4. مقارنة مع UserProfile واقتراح تحديثات
```

### سيناريو 3: بحث بالمهارات

```csharp
// في .NET Controller
var pythonDevelopers = await _context.ModelExtrations
    .Where(m => m.Skills.Contains("Python"))
    .ToListAsync();
```

---

## 🎯 خطط مستقبلية

- [ ] إضافة OCR للـ CVs المصورة
- [ ] تحسين دقة استخراج التواريخ
- [ ] دعم لغات إضافية (عربي، فرنسي، إلخ)
- [ ] مقارنة تلقائية بين ModelExtration و UserProfile
- [ ] اقتراح تحديثات للملف الشخصي
- [ ] تحليل جودة CV وإعطاء توصيات

---

## 📄 الترخيص

MIT License

---

## 🤝 المساهمة

مرحب بأي مساهمات! افتح Issue أو Pull Request

---

## 📞 الدعم

للمشاكل أو الأسئلة:
- افتح Issue في GitHub
- راجع التوثيق في `/docs`
- تحقق من Logs

---

**Built with ❤️ for Career Path**
