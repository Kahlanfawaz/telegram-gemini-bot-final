import requests
import os
import sys

# الحصول على المتغيرات من البيئة
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VERCEL_DOMAIN = os.getenv("VERCEL_DOMAIN")

if not TELEGRAM_BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    sys.exit(1)

if not VERCEL_DOMAIN:
    print("Error: VERCEL_DOMAIN environment variable not set. Please set it to your Vercel domain (e.g., my-bot.vercel.app).")
    sys.exit(1)

# بناء رابط Webhook
WEBHOOK_URL = f"https://{VERCEL_DOMAIN}/{TELEGRAM_BOT_TOKEN}"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

# إرسال الطلب لتعيين Webhook
try:
    response = requests.post(TELEGRAM_API_URL, json={"url": WEBHOOK_URL})
    response.raise_for_status() # رفع استثناء لأكواد الحالة 4xx/5xx
    
    result = response.json()
    
    if result.get("ok"):
        print("Webhook set successfully!")
        print(f"Webhook URL: {WEBHOOK_URL}")
        print(f"Telegram API Response: {result}")
    else:
        print("Failed to set Webhook.")
        print(f"Telegram API Response: {result}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while connecting to Telegram API: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
