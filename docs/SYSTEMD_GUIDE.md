# دليل Ubuntu الكامل لتشغيل البوت بـ systemd

هذا الدليل هو أبسط طريقة Production لتشغيل بوتات Python على VPS بدون `screen`، مع إعادة تشغيل تلقائية بعد إعادة تشغيل السيرفر أو تعطل العملية.

## لماذا `systemd` أفضل من `screen`؟

- تشغيل تلقائي بعد reboot
- إعادة تشغيل تلقائية عند crash
- إدارة موحدة عبر `systemctl`
- متابعة Logs بسهولة عبر `journalctl`

---

## 1) الاتصال بالسيرفر

```bash
ssh your_user@your_vps_ip
```

## 2) تثبيت المتطلبات

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

## 3) الدخول لمجلد المشروع

```bash
cd /path/to/to_drive_uploader
```

## 4) إعداد البيئة الافتراضية وتنزيل المكتبات

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## 5) تجهيز ملف البيئة `.env`

المشروع يقرأ الإعدادات من `.env` عبر `load_dotenv()`، لذلك تأكد أن الملف موجود في جذر المشروع.

تأكد أن `.env` يحتوي المتغيرات المطلوبة:

- `API_ID`
- `API_HASH`
- `PHONE`
- `SESSION`
- `BOT_TOKEN`
- `OWNER_ID`
- `MEDIA_CHANNEL_ID`
- `CREDENTIALS_FILE`
- `REFRESH_TOKEN_FILE`

وتأكد أن الملفات المشار لها موجودة (مثل):

- `credentials/credentials.json`
- `credentials/refresh_token.txt`

---

## 6) إنشاء خدمة systemd

أنشئ الملف:

```bash
sudo nano /etc/systemd/system/to_drive_uploader.service
```

### الخيار الموصى به (آمن - مستخدم مخصص)

```ini
[Unit]
Description=To Drive Uploader Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/to_drive_uploader
EnvironmentFile=/home/botuser/to_drive_uploader/.env
ExecStart=/home/botuser/to_drive_uploader/.venv/bin/python /home/botuser/to_drive_uploader/bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### الخيار السريع (إذا المشروع داخل `/root`)

```ini
[Unit]
Description=To Drive Uploader Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/to_drive_uploader
EnvironmentFile=/root/to_drive_uploader/.env
ExecStart=/root/to_drive_uploader/.venv/bin/python /root/to_drive_uploader/bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

احفظ الملف ثم اخرج.

---

## 7) تفعيل وتشغيل الخدمة

```bash
sudo systemctl daemon-reload
sudo systemctl enable to_drive_uploader
sudo systemctl start to_drive_uploader
```

## 8) التأكد من الحالة

```bash
sudo systemctl status to_drive_uploader
```

النتيجة المطلوبة:

- `active (running)`

## 9) متابعة السجلات (Logs)

```bash
sudo journalctl -u to_drive_uploader -f
```

---

## أوامر يومية مهمة

تشغيل:

```bash
sudo systemctl start to_drive_uploader
```

إيقاف:

```bash
sudo systemctl stop to_drive_uploader
```

إعادة تشغيل:

```bash
sudo systemctl restart to_drive_uploader
```

تعطيل التشغيل التلقائي مع الإقلاع:

```bash
sudo systemctl disable to_drive_uploader
```

---

## بعد أي تعديل في ملف الخدمة

إذا عدلت `/etc/systemd/system/to_drive_uploader.service` نفذ دائمًا:

```bash
sudo systemctl daemon-reload
sudo systemctl restart to_drive_uploader
```

---

## نشر تحديثات الكود (روتين سريع)

داخل مجلد المشروع:

```bash
cd /path/to/to_drive_uploader
source .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart to_drive_uploader
```

---

## مشاكل شائعة وحلها

### الخدمة لا تعمل

افحص:

```bash
sudo systemctl status to_drive_uploader
sudo journalctl -u to_drive_uploader -n 100 --no-pager
```

### خطأ: ملف `.env` غير موجود

- تأكد من المسار في `EnvironmentFile=...`
- تأكد أن الملف موجود فعلا في نفس المسار

### خطأ: Python أو venv غير موجود

- تأكد من المسار داخل `ExecStart=...`
- يجب أن يكون الملف التنفيذي موجودا:
  - `/path/to/project/.venv/bin/python`

### الخدمة تعمل ثم تتوقف فورًا

- غالبا متغير بيئة ناقص أو خطأ في الكود
- راجع `journalctl` وستظهر تفاصيل الخطأ

---

## تشغيل عدة بوتات بنفس الأسلوب

لكل بوت:

1. مجلد مشروع مستقل
2. `.venv` مستقل
3. ملف خدمة مستقل باسم مختلف، مثال:
   - `to_drive_uploader.service`
   - `orders_bot.service`
4. فعّل كل خدمة:
   - `daemon-reload`
   - `enable`
   - `start`

---

## خلاصة

باستخدام `systemd` لن تحتاج مراقبة يدوية مثل `screen`:

- البوت يشتغل تلقائيًا بعد reboot
- يعيد التشغيل تلقائيًا عند التعطل
- إدارة واضحة وسريعة من مكان واحد

---

## Update Workflow (تطبيق التحديثات)

### الحالة العادية: تحديث كود البوت

بعد أي تحديث للكود، نفّذ:

```bash
cd /path/to/to_drive_uploader
git pull
sudo systemctl restart to_drive_uploader
sudo systemctl status to_drive_uploader
```

### إذا التحديث يحتوي مكتبات جديدة

نفّذ:

```bash
cd /path/to/to_drive_uploader
git pull
source .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart to_drive_uploader
sudo systemctl status to_drive_uploader
```

### إذا عدّلت ملف الخدمة نفسه

إذا عدّلت:

- `/etc/systemd/system/to_drive_uploader.service`

فلازم تعمل:

```bash
sudo systemctl daemon-reload
sudo systemctl restart to_drive_uploader
sudo systemctl status to_drive_uploader
```

### التحقق الفوري بعد أي تحديث

```bash
sudo journalctl -u to_drive_uploader -f
```

إذا ظهرت مشكلة بعد تحديث:

- تحقق من dependencies (`pip install -r requirements.txt`)
- تحقق من متغيرات البيئة داخل `.env`
