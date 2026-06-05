"""Send messages to a Telegram chat via a bot.

Set the following environment variables (locally via a .env file, or as
GitHub Actions secrets in CI):

    TELEGRAM_BOT_TOKEN  - token from @BotFather
    TELEGRAM_CHAT_ID    - the chat/channel ID to post into
"""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
REQUEST_TIMEOUT = 30
# Telegram caps messages at 4096 characters.
MAX_MESSAGE_LEN = 4096


def send_message(text: str) -> None:
    """Send ``text`` to the configured Telegram chat."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set."
        )

    payload = {
        "chat_id": chat_id,
        "text": text[:MAX_MESSAGE_LEN],
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    response = requests.post(
        TELEGRAM_API.format(token=token), data=payload, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    print("Telegram notification sent.")


if __name__ == "__main__":
    send_message("✅ Test message from job-hunter-automation.")
