# Job Hunter Automation

Automatically fetches recent remote job postings and sends them to a Telegram
chat on a schedule via GitHub Actions.

## How it works

1. [`src/fetch_jobs.py`](src/fetch_jobs.py) queries the free
   [Remotive API](https://remotive.com/api/remote-jobs) for jobs matching your
   search term.
2. [`src/telegram_notify.py`](src/telegram_notify.py) posts the results to your
   Telegram chat using a bot.
3. [`.github/workflows/jobs.yml`](.github/workflows/jobs.yml) runs the whole
   thing daily (and on demand).

## Setup

### 1. Create a Telegram bot

1. Message [@BotFather](https://t.me/BotFather) and run `/newbot`.
2. Copy the **bot token** it gives you.
3. Start a chat with your bot, then get your **chat ID** (e.g. via
   [@userinfobot](https://t.me/userinfobot)).

### 2. Run locally

```bash
cd job-hunter-automation
pip install -r src/requirements.txt

# Configure credentials (create a .env file in the repo root)
echo "TELEGRAM_BOT_TOKEN=your-token"   >> .env
echo "TELEGRAM_CHAT_ID=your-chat-id"   >> .env

# Optional tuning
export SEARCH_QUERY="python developer"
export MAX_JOBS=10

python src/fetch_jobs.py
```

### 3. Run on GitHub Actions

Add the following in your repository settings:

| Type   | Name                 | Value                       |
| ------ | -------------------- | --------------------------- |
| Secret | `TELEGRAM_BOT_TOKEN` | Your bot token              |
| Secret | `TELEGRAM_CHAT_ID`   | Your chat ID                |
| Var    | `SEARCH_QUERY`       | Job search term (optional)  |
| Var    | `MAX_JOBS`           | Max jobs per run (optional) |

The workflow runs daily at 08:00 UTC. Trigger it manually any time from the
**Actions** tab via **Run workflow**.

## Configuration

| Variable             | Default  | Description                          |
| -------------------- | -------- | ------------------------------------ |
| `TELEGRAM_BOT_TOKEN` | —        | Telegram bot token (required)        |
| `TELEGRAM_CHAT_ID`   | —        | Telegram chat ID (required)          |
| `SEARCH_QUERY`       | `python` | Term used to filter job postings     |
| `MAX_JOBS`           | `10`     | Maximum number of jobs per run       |

## License

MIT
