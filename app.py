import os
import logging
import json
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai.errors import APIError

# إعداد التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# المتغيرات العامة التي سيتم تهيئتها لاحقًا
application = None
client = None
TELEGRAM_BOT_TOKEN = None
GEMINI_API_KEY = None
GEMINI_MODEL = "gemini-2.5-flash"

# قاموس لتخزين جلسات المحادثة (Chat Sessions)
chat_sessions = {}

# دوال معالجة الأوامر والرسائل
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يرسل رسالة ترحيب عند إصدار الأمر /start ويبدأ جلسة محادثة جديدة."""
    global chat_sessions
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # بدء جلسة محادثة جديدة
    chat_sessions[chat_id] = client.chats.create(model=GEMINI_MODEL)
    
    await update.message.reply_html(
        f"مرحباً {user.mention_html()}! أنا بوت يعمل بتقنية Gemini AI. لقد بدأت جلسة محادثة جديدة. أرسل لي أي سؤال وسأجيبك.",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يرد على رسالة المستخدم باستخدام نموذج Gemini مع الحفاظ على سياق المحادثة وباستخدام Streaming."""
    global client, chat_sessions
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    # إرسال مؤشر الكتابة (typing)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # التحقق من وجود جلسة محادثة، وإذا لم توجد، يتم إنشاؤها
    if chat_id not in chat_sessions:
        # إعادة تهيئة العميل إذا لم يكن مهيأ (في حالة نادرة)
        if client is None:
            init_application()
        
        # إنشاء جلسة محادثة جديدة
        chat_sessions[chat_id] = client.chats.create(model=GEMINI_MODEL)
        
    chat = chat_sessions[chat_id]

    try:
        # إرسال رسالة أولية لإعطاء معرف للرسالة التي سيتم تحديثها
        initial_message = await update.message.reply_text("...")
        message_id = initial_message.message_id
        
        full_response = ""
        
        # استخدام Streaming
        response_stream = chat.send_message_stream(user_message)
        
        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                # تحديث الرسالة كلما توفر جزء جديد (لتحسين الأداء، يمكن التحديث كل بضعة أجزاء)
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=full_response + "▌" # إضافة مؤشر كتابة مؤقت
                )
        
        # إزالة مؤشر الكتابة المؤقت بعد اكتمال الرد
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=full_response
        )

    except APIError as e:
        logger.error(f"Gemini API Error: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="عذراً، حدث خطأ أثناء الاتصال بخدمة Gemini AI. يرجى المحاولة مرة أخرى لاحقاً."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="عذراً، حدث خطأ غير متوقع. يرجى التحقق من سجلات البوت."
        )

# دالة لتهيئة التطبيق (تُستدعى مرة واحدة)
def init_application():
    """تهيئة Application و Gemini Client."""
    global application, client, TELEGRAM_BOT_TOKEN, GEMINI_API_KEY
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        logger.error("TELEGRAM_BOT_TOKEN or GEMINI_API_KEY environment variable not set.")
        return

    # تهيئة عميل Gemini
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error configuring Gemini client: {e}")
        return

    # إعداد تطبيق Telegram.ext
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Application and Gemini Client initialized successfully.")

# إعداد تطبيق Flask لاستقبال Webhooks
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """نقطة نهاية بسيطة للتحقق من حالة التطبيق."""
    return "Telegram Gemini Bot is running!", 200

@app.route("/ping", methods=["GET"])
def ping():
    """نقطة نهاية تستخدم لمنع الخادم من الدخول في وضع السكون (Cold Start)."""
    return "pong", 200

@app.route(f"/{os.getenv('TELEGRAM_BOT_TOKEN')}", methods=["POST"])
async def webhook_handler():
    """نقطة نهاية Webhook لمعالجة تحديثات تليجرام."""
    global application
    
    # تهيئة التطبيق إذا لم يكن مهيأ بعد
    if application is None:
        init_application()
        
    if application is None:
        return jsonify({"status": "error", "message": "Application not initialized"}), 500

    if request.method == "POST":
        # قراءة البيانات المرسلة من تليجرام
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # معالجة التحديث
        await application.process_update(update)
        
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

# 5. دالة رئيسية للتشغيل المحلي (اختياري)
def main() -> None:
    """تشغيل البوت في وضع Polling للتشغيل المحلي."""
    init_application()
    if application:
        logger.info("Starting bot in Polling mode for local testing...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # هذا الجزء مخصص للتشغيل المحلي فقط
    # main()
    # للتشغيل على Vercel، سيتم استدعاء التطبيق مباشرة
    pass
