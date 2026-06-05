"""Send the real job digest to Telegram, grouped into India + Foreign (WFH).

Reads jobs via fetch_jobs.get_jobs() and posts them to the configured chat.
Long digests are split into multiple messages to stay under Telegram's
4096-character limit.
"""

import os

import requests

from fetch_jobs import GROUP_FOREIGN, GROUP_INDIA, get_jobs

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

REQUEST_TIMEOUT = 30
# Stay comfortably below Telegram's 4096-char hard limit.
MAX_MESSAGE_LEN = 3800


def send_message(text: str) -> None:
    """Send a single text message to the Telegram chat."""
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()


def render_job(index: int, job: dict) -> str:
    """Render a single job as a text block."""
    return (
        f"{index}. {job['title']}\n"
        f"🏢 {job['company']}\n"
        f"🌍 {job['location']}  ·  {job['source']}\n"
        f"🔗 {job['url']}"
    )


def build_digest(jobs: list[dict]) -> list[str]:
    """Build the digest as section blocks (India first, then Foreign WFH)."""
    blocks: list[str] = []

    india = [j for j in jobs if j.get("group") == GROUP_INDIA]
    foreign = [j for j in jobs if j.get("group") == GROUP_FOREIGN]

    if india:
        blocks.append(f"📍 *India Jobs* ({len(india)})")
        blocks.extend(render_job(i, j) for i, j in enumerate(india, start=1))
    if foreign:
        blocks.append(f"🌐 *Foreign Jobs — Work From Home* ({len(foreign)})")
        blocks.extend(render_job(i, j) for i, j in enumerate(foreign, start=1))

    return blocks


def chunk_blocks(header: str, blocks: list[str]) -> list[str]:
    """Group blocks into messages under the size limit."""
    messages = []
    current = header
    for block in blocks:
        if len(current) + len(block) + 2 > MAX_MESSAGE_LEN:
            messages.append(current.rstrip())
            current = ""
        current += block + "\n\n"
    if current.strip():
        messages.append(current.rstrip())
    return messages


def main() -> None:
    jobs = get_jobs()

    if not jobs:
        send_message(
            "🔎 Himanshu Daily Job Digest\n\n"
            "No matching jobs found right now. Will check again next run."
        )
        print("No jobs found — sent empty-state message.")
        return

    header = f"🔥 Himanshu Daily Job Digest\n{len(jobs)} matching job(s) found\n\n"
    for message in chunk_blocks(header, build_digest(jobs)):
        send_message(message)

    print(f"Telegram digest sent ({len(jobs)} jobs).")


if __name__ == "__main__":
    main()
