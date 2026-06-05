import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

message = """
🚀 Job Automation Status

✅ GitHub Actions Working
✅ Google Sheets Connected
✅ Telegram Connected

Next Step:
Fetch real jobs from free job APIs.
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(
    url,
    json={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("Telegram message sent")
