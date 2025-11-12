# 📖 دليل التثبيت المفصل - بوت إدارة التخطيط

## 🎯 المتطلبات الأساسية

### 1. المتطلبات التقنية
- **نظام التشغيل**: Linux, macOS, أو Windows
- **Python**: الإصدار 3.8 أو أحدث
- **الذاكرة**: 512 MB على الأقل
- **المساحة**: 100 MB على الأقل

### 2. حساب تليغرام
- حساب تليغرام نشط
- إمكانية الوصول إلى [@BotFather](https://t.me/BotFather)

---

## 📥 طريقة 1: التثبيت التلقائي (الأسهل)

### على Linux/Mac

```bash
# 1. الانتقال لمجلد البوت
cd /home/user/telegram_bot

# 2. إعطاء صلاحية التنفيذ لسكريبت التثبيت
chmod +x setup.sh

# 3. تشغيل سكريبت التثبيت
./setup.sh
```

### على Windows

```powershell
# 1. الانتقال لمجلد البوت
cd C:\Users\YourName\telegram_bot

# 2. تشغيل التثبيت
python setup_windows.py
```

---

## 🔧 طريقة 2: التثبيت اليدوي (المفصل)

### الخطوة 1: تثبيت Python

#### على Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### على CentOS/RHEL
```bash
sudo yum install python3 python3-pip
```

#### على macOS
```bash
# باستخدام Homebrew
brew install python3
```

#### على Windows
1. تنزيل Python من [python.org](https://www.python.org/downloads/)
2. تشغيل المثبت (تأكد من تحديد "Add Python to PATH")

### الخطوة 2: إنشاء بيئة افتراضية (موصى به)

```bash
# إنشاء بيئة افتراضية
python3 -m venv venv

# تفعيل البيئة الافتراضية
# على Linux/Mac:
source venv/bin/activate

# على Windows:
venv\Scripts\activate
```

### الخطوة 3: تثبيت المكتبات

```bash
pip install -r requirements.txt
```

في حالة وجود مشاكل، ثبت المكتبات بشكل منفصل:

```bash
pip install python-telegram-bot==20.7
pip install sqlalchemy==2.0.23
pip install python-dotenv==1.0.0
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install reportlab==4.0.7
```

### الخطوة 4: إنشاء البوت على تليغرام

1. **افتح [@BotFather](https://t.me/BotFather) على تليغرام**

2. **أرسل الأمر** `/newbot`

3. **اختر اسم البوت**
   ```
   مثال: بوت إدارة التخطيط - البريقة
   ```

4. **اختر معرف البوت** (يجب أن ينتهي بـ bot)
   ```
   مثال: BuraigaPlanningBot
   ```

5. **احفظ التوكن** الذي سيرسله لك BotFather
   ```
   مثال: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. **إعدادات إضافية (اختيارية)**
   - إضافة صورة: `/setuserpic`
   - إضافة وصف: `/setdescription`
   - إضافة أوامر: `/setcommands`

### الخطوة 5: إعداد ملف الإعدادات

```bash
# انسخ ملف المثال
cp .env.example .env

# افتح الملف للتحرير
nano .env  # أو استخدم محرر نصوص آخر
```

**محتوى ملف .env:**
```env
# توكن البوت
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# قاعدة البيانات (SQLite للبداية)
DATABASE_URL=sqlite:///buraiga_planning.db
```

### الخطوة 6: تهيئة قاعدة البيانات

```bash
python database.py
```

يجب أن ترى الرسالة:
```
✅ تم إنشاء قاعدة البيانات بنجاح
```

### الخطوة 7: إنشاء مجلد الملفات

```bash
mkdir uploads
```

### الخطوة 8: تشغيل البوت

```bash
python main.py
```

يجب أن ترى:
```
🔧 تهيئة قاعدة البيانات...
✅ تم تهيئة قاعدة البيانات
🤖 بدء تشغيل البوت...
✅ البوت جاهز للعمل!
📱 رابط البوت: https://t.me/YOUR_BOT_USERNAME
```

---

## 🗄️ إعداد قاعدة بيانات PostgreSQL (للإنتاج)

### 1. تثبيت PostgreSQL

#### على Ubuntu/Debian
```bash
sudo apt install postgresql postgresql-contrib
```

#### على macOS
```bash
brew install postgresql
```

### 2. إنشاء قاعدة البيانات

```bash
# الدخول لـ PostgreSQL
sudo -u postgres psql

# إنشاء قاعدة بيانات
CREATE DATABASE buraiga_db;

# إنشاء مستخدم
CREATE USER buraiga_user WITH PASSWORD 'strong_password';

# إعطاء الصلاحيات
GRANT ALL PRIVILEGES ON DATABASE buraiga_db TO buraiga_user;

# الخروج
\q
```

### 3. تثبيت مكتبة PostgreSQL

```bash
pip install psycopg2-binary
```

### 4. تحديث ملف .env

```env
DATABASE_URL=postgresql://buraiga_user:strong_password@localhost:5432/buraiga_db
```

---

## 🚀 تشغيل البوت في الخلفية

### طريقة 1: استخدام nohup

```bash
nohup python main.py > bot.log 2>&1 &

# لعرض السجلات
tail -f bot.log

# لإيقاف البوت
ps aux | grep main.py
kill <PID>
```

### طريقة 2: استخدام systemd (Linux)

**1. إنشاء ملف الخدمة:**

```bash
sudo nano /etc/systemd/system/buraiga-bot.service
```

**2. محتوى الملف:**

```ini
[Unit]
Description=Buraiga Planning Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram_bot
Environment="PATH=/path/to/telegram_bot/venv/bin"
ExecStart=/path/to/telegram_bot/venv/bin/python /path/to/telegram_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. تفعيل وتشغيل الخدمة:**

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة
sudo systemctl enable buraiga-bot

# بدء الخدمة
sudo systemctl start buraiga-bot

# فحص الحالة
sudo systemctl status buraiga-bot

# عرض السجلات
sudo journalctl -u buraiga-bot -f
```

**4. أوامر مفيدة:**

```bash
# إيقاف الخدمة
sudo systemctl stop buraiga-bot

# إعادة تشغيل
sudo systemctl restart buraiga-bot

# تعطيل التشغيل التلقائي
sudo systemctl disable buraiga-bot
```

### طريقة 3: استخدام screen

```bash
# تثبيت screen
sudo apt install screen

# إنشاء جلسة جديدة
screen -S buraiga_bot

# تشغيل البوت
python main.py

# الانفصال عن الجلسة: اضغط Ctrl+A ثم D

# العودة للجلسة
screen -r buraiga_bot

# عرض الجلسات النشطة
screen -ls
```

---

## 🔐 الأمان والحماية

### 1. حماية ملف .env

```bash
# تقييد الصلاحيات
chmod 600 .env

# تأكد من عدم رفعه لـ Git
echo ".env" >> .gitignore
```

### 2. جدار حماية (Firewall)

```bash
# السماح فقط بـ SSH والبوت
sudo ufw allow ssh
sudo ufw enable
```

### 3. تحديثات أمنية

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade

# تحديث المكتبات
pip install --upgrade -r requirements.txt
```

---

## 📊 النسخ الاحتياطي

### 1. نسخ احتياطي لقاعدة البيانات SQLite

```bash
# نسخ يدوي
cp buraiga_planning.db backup_$(date +%Y%m%d).db

# نسخ تلقائي يومي (cron)
0 2 * * * cp /path/to/buraiga_planning.db /path/to/backups/backup_$(date +\%Y\%m\%d).db
```

### 2. نسخ احتياطي PostgreSQL

```bash
# نسخ يدوي
pg_dump buraiga_db > backup_$(date +%Y%m%d).sql

# نسخ تلقائي (cron)
0 2 * * * pg_dump buraiga_db > /path/to/backups/backup_$(date +\%Y\%m\%d).sql
```

### 3. استعادة النسخة الاحتياطية

```bash
# SQLite
cp backup_20250101.db buraiga_planning.db

# PostgreSQL
psql buraiga_db < backup_20250101.sql
```

---

## 🧪 الاختبار

### 1. اختبار الاتصال

افتح البوت على تليغرام وأرسل `/start`

### 2. إنشاء مستخدم تجريبي

سيطلب منك البوت إدخال معلوماتك

### 3. اختبار الميزات

- إضافة خطة تجريبية
- إضافة مشروع تجريبي
- استخراج تقرير

---

## ❓ حل المشاكل الشائعة

### المشكلة: البوت لا يستجيب

**الحل:**
```bash
# تحقق من السجلات
tail -f bot.log

# تحقق من التوكن
cat .env | grep BOT_TOKEN

# تحقق من الاتصال بالإنترنت
ping telegram.org
```

### المشكلة: خطأ في قاعدة البيانات

**الحل:**
```bash
# حذف وإعادة إنشاء قاعدة البيانات
rm buraiga_planning.db
python database.py
```

### المشكلة: خطأ في تثبيت المكتبات

**الحل:**
```bash
# تحديث pip
pip install --upgrade pip

# تثبيت المكتبات واحدة واحدة
pip install python-telegram-bot
pip install sqlalchemy
# وهكذا...
```

### المشكلة: خطأ في الصلاحيات

**الحل:**
```bash
# إعطاء صلاحيات للمجلد
chmod -R 755 telegram_bot

# إعطاء صلاحيات للملفات
chmod 644 *.py
```

---

## 📞 الدعم الفني

في حالة وجود مشاكل:

1. راجع ملف `README.md`
2. تحقق من السجلات `bot.log`
3. راجع قسم حل المشاكل أعلاه

---

## ✅ قائمة التحقق النهائية

- [ ] تثبيت Python 3.8+
- [ ] تثبيت جميع المكتبات
- [ ] إنشاء بوت على تليغرام
- [ ] حفظ التوكن في .env
- [ ] تهيئة قاعدة البيانات
- [ ] إنشاء مجلد uploads
- [ ] تشغيل البوت
- [ ] اختبار البوت على تليغرام
- [ ] إعداد النسخ الاحتياطي
- [ ] إعداد التشغيل في الخلفية

---

🎉 **تهانينا! البوت جاهز للاستخدام!**
