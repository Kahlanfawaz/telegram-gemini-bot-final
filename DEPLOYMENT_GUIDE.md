# دليل نشر بوت تليجرام على Vercel (الإصدار المحسن)

هذا الدليل يوضح كيفية نشر بوت تليجرام الذي يعمل بتقنية Gemini AI على منصة **Vercel** مجانًا، مع دعم **المحادثات المستمرة (Chat History)** واستخدام سكربت لتعيين **Webhooks** تلقائيًا.

## التحسينات الجديدة

*   **دعم المحادثات المستمرة:** البوت الآن يحفظ سياق المحادثة لكل مستخدم، مما يجعله أكثر ذكاءً في الردود المتتابعة.
*   **إصلاح مشكلة النشر:** تم تعديل الكود لتأجيل تهيئة البوت إلى مرحلة التشغيل، مما يحل مشكلة `InvalidToken` أثناء البناء على Vercel.
*   **سكربت تعيين Webhook:** تم توفير سكربت `set_webhook.py` لتعيين Webhook تلقائيًا، مما يقلل من الأخطاء اليدوية.

## المتطلبات

1.  حساب **GitHub** أو **GitLab** أو **Bitbucket**.
2.  حساب **Vercel** (يمكن التسجيل باستخدام حساب GitHub).
3.  توكن بوت تليجرام (`TELEGRAM_BOT_TOKEN`).
4.  مفتاح Gemini API (`GEMINI_API_KEY`).

## الخطوة 1: رفع المشروع إلى GitHub

تم رفع الملفات المعدلة إلى المستودع: [https://github.com/Kahlanfawaz/telegram-gemini-bot-vercel](https://github.com/Kahlanfawaz/telegram-gemini-bot-vercel)

## الخطوة 2: النشر على Vercel

1.  **ربط المستودع:**
    *   سجل الدخول إلى حسابك في Vercel.
    *   انقر على **"Add New..."** ثم **"Project"**.
    *   اختر المستودع `telegram-gemini-bot-vercel`.
    *   انقر على **"Import"**.

2.  **إضافة متغيرات البيئة:**
    أضف المتغيرات التالية كمتغيرات بيئة **سرية (Secret Environment Variables)**:

    | الاسم (Name) | القيمة (Value) |
    | :--- | :--- |
    | `TELEGRAM_BOT_TOKEN` | توكن البوت الخاص بك. |
    | `GEMINI_API_KEY` | مفتاح Gemini API الخاص بك. |

3.  **النشر (Deploy):**
    *   انقر على **"Deploy"**.
    *   انتظر حتى تكتمل عملية النشر. بمجرد الانتهاء، ستحصل على رابط (Domain) لمشروعك (مثال: `https://my-gemini-bot.vercel.app`). **احفظ هذا الرابط.**

## الخطوة 3: تعيين Webhook تلقائيًا (الخطوة الحاسمة)

بدلاً من تعيين Webhook يدويًا، سنستخدم السكربت `set_webhook.py` لضمان الدقة.

1.  **الحصول على رابط Vercel:**
    افترض أن رابط مشروعك هو: `my-gemini-bot-vercel.vercel.app`

2.  **تشغيل السكربت محليًا:**
    قم بتشغيل السكربت `set_webhook.py` على جهازك المحلي (بعد تثبيت المكتبات وتفعيل البيئة الافتراضية) باستخدام متغيرات البيئة التالية:

    ```bash
    # استبدل القيم بقيمك الفعلية
    export TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    export VERCEL_DOMAIN="YOUR_VERCEL_DOMAIN.vercel.app" 
    
    # تأكد من أنك في مجلد المشروع
    python3 set_webhook.py
    ```

    **مثال عملي:**
    ```bash
    export TELEGRAM_BOT_TOKEN="8291744408:AAFZFwOvBBE-X5MIHUzapZ0X5u6_I9fOqkg"
    export VERCEL_DOMAIN="my-gemini-bot-vercel.vercel.app" 
    python3 set_webhook.py
    ```

    إذا نجح الأمر، ستحصل على رسالة: `Webhook set successfully!`

## الخطوة 4: اختبار البوت

الآن، يمكنك العودة إلى تليجرام وإرسال رسالة إلى البوت الخاص بك. يجب أن يعمل بشكل مستقر مع حفظ سياق المحادثة.

---
**ملاحظة:** إذا واجهت أي مشاكل، يمكنك دائمًا التحقق من سجلات (Logs) مشروعك على Vercel.
