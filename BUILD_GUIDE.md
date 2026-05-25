# 🕷 JoCkEeRe Ultra Scanner v2.0 — دليل بناء APK

## ما الذي تغيّر في النسخة الجديدة؟

### ✨ تحسينات المظهر
- **تصميم Dark Theme** متطور مع ألوان متدرجة (Neon Blue + Purple + Pink)
- **Glow Buttons** — أزرار مضيئة مع تأثير توهج عند الضغط
- **Card Layout** — كل قسم في بطاقة مستقلة بزوايا مدورة
- **StatBox** — إحصائيات HITS / CHECKED / PROGRESS بواجهة بيانية
- **Section Headers** — عناوين أقسام بشريط جانبي ملوّن
- **طابع زمني** في كل سطر من سجل الفحص
- **Status Bar** محسّن مع ألوان تتغير بحسب الحالة (أخضر/أصفر/أحمر)
- **Popup نتائج** أنيق عند انتهاء الفحص

### 🔧 تحسينات وظيفية
- تنظيم معاملات الـ panel في dictionary بدلاً من if/elif المتكررة
- إصلاح `real` variable scope في `scan_worker`
- إضافة timestamp لكل رسالة في السجل
- عداد الأسطر في نافذة السجل
- رسائل أوضح عند الأخطاء والأحداث

---

## 🚀 طريقة بناء APK

### الطريقة 1: Google Colab (الأسهل - مجاني)

```python
# في Google Colab
!pip install buildozer
!sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
!pip install cython

# ارفع ملفات المشروع ثم:
%cd /content/jockeere_scanner
!buildozer android debug
```

### الطريقة 2: Linux / WSL

```bash
# تثبيت المتطلبات
sudo apt update && sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libffi-dev libssl-dev
pip install buildozer cython

# بناء APK
cd jockeere_scanner
buildozer android debug

# ستجد الـ APK في:
# bin/jockeere-2.0-arm64-v8a_armeabi-v7a-debug.apk
```

### الطريقة 3: Docker (أسهل على Windows)

```bash
docker pull kivy/buildozer
docker run --volume "$(pwd)":/home/user/hostcwd kivy/buildozer android debug
```

---

## 📱 تركيب الـ APK

1. انسخ ملف `*.apk` إلى هاتفك
2. من الإعدادات: فعّل **"تثبيت من مصادر غير معروفة"**
3. افتح الملف وثبّته
4. عند أول تشغيل: اقبل طلب الأذونات (Storage + Internet)

---

## 📂 هيكل المشروع

```
jockeere_scanner/
├── main.py          ← الكود الرئيسي (هذا الملف)
├── buildozer.spec   ← إعدادات البناء
└── BUILD_GUIDE.md   ← هذا الدليل
```

---

## ⚠️ ملاحظات مهمة

- **Hits** تُحفظ في: `/sdcard/Hits/JoCkEeRe/`
- **Combo files** تُوضع في: `/sdcard/combo/`
- **Config** يُحفظ تلقائياً في: `/sdcard/Hits/jockeere_config.json`
- إذا فشل `cfscrape` يرجع إلى `requests.Session()` عادي

---

*JoCkEeRe Ultra Scanner v2.0 — Enhanced UI Edition*
