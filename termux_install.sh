#!/data/data/com.termux/files/usr/bin/bash

# سكريبت تثبيت بوت إدارة التخطيط على Termux
# لهواتف الأندرويد

echo "╔════════════════════════════════════════════════════════╗"
echo "║   🏢 بوت إدارة التخطيط - شركة البريقة               ║"
echo "║   📱 سكريبت التثبيت على Termux                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# التحقق من Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo "❌ هذا السكريبت مخصص لـ Termux فقط!"
    exit 1
fi

echo "🔧 الخطوة 1/6: تحديث الحزم..."
pkg update -y && pkg upgrade -y

echo ""
echo "📦 الخطوة 2/6: تثبيت Python و Git..."
pkg install python git libxml2 libxslt -y

echo ""
echo "📂 الخطوة 3/6: إعداد مجلد البوت..."
cd ~
mkdir -p buraiga-bot
cd buraiga-bot

echo ""
echo "📥 الخطوة 4/6: تحميل ملفات البوت..."
echo ""
echo "⚠️  تنبيه مهم:"
echo "1. ضع ملف telegram_bot_complete.tar.gz في مجلد Downloads"
echo "2. أو استخدم git clone إذا رفعت على GitHub"
echo ""
read -p "هل الملف موجود في Downloads؟ (y/n): " file_exists

if [ "$file_exists" = "y" ] || [ "$file_exists" = "Y" ]; then
    echo "📦 نسخ الملف من Downloads..."
    cp ~/storage/downloads/telegram_bot_complete.tar.gz .
    
    echo "📦 فك الضغط..."
    tar -xzf telegram_bot_complete.tar.gz
    cd telegram_bot
else
    echo ""
    read -p "هل رفعت المشروع على GitHub؟ (y/n): " github_exists
    
    if [ "$github_exists" = "y" ] || [ "$github_exists" = "Y" ]; then
        read -p "أدخل رابط المستودع (https://github.com/...): " repo_url
        git clone $repo_url
        cd buraiga-planning-bot 2>/dev/null || cd telegram_bot
    else
        echo "❌ الرجاء تحميل الملفات أولاً!"
        echo ""
        echo "الخيارات:"
        echo "1. ضع ملف telegram_bot_complete.tar.gz في مجلد Downloads"
        echo "2. أو ارفع المشروع على GitHub واستخدم git clone"
        exit 1
    fi
fi

echo ""
echo "⚙️  الخطوة 5/6: إعداد البوت..."
echo ""

# إنشاء ملف .env
if [ ! -f .env ]; then
    cp .env.example .env
    
    echo "🔑 يرجى إدخال توكن البوت من @BotFather:"
    read -p "التوكن: " bot_token
    
    sed -i "s/YOUR_BOT_TOKEN_HERE/$bot_token/" .env
    
    echo "✅ تم حفظ التوكن"
fi

echo ""
echo "📚 الخطوة 6/6: تثبيت المكتبات..."
echo "⏳ قد تستغرق 5-10 دقائق..."
echo ""

pip install -r requirements.txt

echo ""
echo "🗄️  تهيئة قاعدة البيانات..."
python database.py

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           ✅ اكتمل التثبيت بنجاح!                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📝 الخطوات التالية:"
echo ""
echo "1️⃣  لتشغيل البوت:"
echo "   python main.py"
echo ""
echo "2️⃣  لتشغيل البوت في الخلفية (موصى به):"
echo "   tmux new -s bot"
echo "   python main.py"
echo "   # للخروج: اضغط Ctrl+B ثم D"
echo ""
echo "3️⃣  للعودة للبوت:"
echo "   tmux attach -t bot"
echo ""
echo "4️⃣  لإيقاف البوت:"
echo "   # داخل tmux اضغط: Ctrl+C"
echo ""
echo "⚠️  ملاحظات مهمة:"
echo "   • البوت سيتوقف عند إغلاق Termux"
echo "   • استخدم tmux للإبقاء عليه يعمل في الخلفية"
echo "   • للاستخدام الفعلي، استخدم خدمة سحابية (راجع ANDROID_GUIDE.md)"
echo ""
echo "📚 للمزيد من المعلومات:"
echo "   cat README.md"
echo "   cat ANDROID_GUIDE.md"
echo ""
echo "🚀 البوت جاهز للعمل!"
echo ""

# إنشاء سكريبت تشغيل سريع
cat > run.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/buraiga-bot/telegram_bot
python main.py
EOF

chmod +x run.sh

echo "💡 نصيحة: يمكنك تشغيل البوت بسرعة بكتابة:"
echo "   ~/buraiga-bot/telegram_bot/run.sh"
echo ""

read -p "هل تريد تشغيل البوت الآن؟ (y/n): " start_now

if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    echo "🚀 تشغيل البوت..."
    echo ""
    python main.py
else
    echo ""
    echo "✅ يمكنك تشغيل البوت لاحقاً بكتابة:"
    echo "   python main.py"
    echo ""
fi
