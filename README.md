# SEX-NSFW-COVER-FINDER

أداة للبحث عن **الغلاف الترويجي الرسمي** (Official Promotional Cover) لمشاهد Bratty Sis / Nubiles / Moms Teach Sex.

الهدف: الحصول على صورة الغلاف الخاصة بـ **مشهد الإعداد الرئيسي** (Setup Scene) وليس لقطات الجنس من داخل الفيديو.

---

## الملفات

| الملف | الوصف |
|------|------|
| `find_cover.py` | السكربت الرئيسي (الأفضل) - يبحث فعلياً في brattyfamily.com ويستخرج `og:image` |
| `index.html` | واجهة ويب بسيطة تعمل مباشرة في المتصفح |
| `README.md` | هذا الملف |

---

## طريقة الاستخدام (الموصى بها)

```bash
# تثبيت المتطلبات (مرة واحدة)
pip install requests beautifulsoup4

# البحث عن أي عنوان
python3 find_cover.py "At Your Service Sis - S3:E5"
python3 find_cover.py "It Just Slipped In"
python3 find_cover.py "Hide And Seek With My Stepsister"
```

السكربت يقوم بـ:
1. تحويل العنوان إلى slug
2. فتح صفحة الحلقة على `brattyfamily.com`
3. استخراج صورة `og:image` الرسمية
4. في حالة الفشل يجرب مسارات الصور المباشرة

---

## الواجهة HTML

افتح ملف `index.html` في أي متصفح.  
مفيدة للأمثلة السريعة، لكنها محدودة بسبب قيود CORS.

---

## ملاحظات مهمة

- الغلاف الجيد = صورة ترويجية لمشهد الإعداد (غسالة، فطور، كنبة...) غالباً تحتوي على لوجو السلسلة.
- لا تأخذ صور الجنس الصريح من وسط المشهد.
- الأداة لأغراض تعليمية فقط.

---

**Repository:** [SEX-NSFW/SEX-NSFW-COVER-FINDER](https://github.com/SEX-NSFW/SEX-NSFW-COVER-FINDER)
