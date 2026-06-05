"""Write real job postings into the connected Google Sheet.

Appends only jobs whose URL is not already present, so re-running daily does
not pile up duplicates. Requires the GOOGLE_CREDENTIALS (service-account JSON)
and GOOGLE_SHEET_ID environment variables.
"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

from fetch_jobs import get_jobs

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADER = ["Group", "Title", "Company", "Location", "Source", "URL"]


def open_sheet():
    creds = Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_CREDENTIALS"]), scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1


def main() -> None:
    sheet = open_sheet()
    existing = sheet.get_all_values()

    # Ensure a header row exists, and collect already-stored URLs.
    if not existing:
        sheet.append_row(HEADER)
        existing_urls: set[str] = set()
    else:
        url_col = len(HEADER) - 1  # URL is the last column
        existing_urls = {
            row[url_col] for row in existing[1:] if len(row) > url_col and row[url_col]
        }

    jobs = get_jobs()
    new_rows = [
        [
            job.get("group", ""),
            job["title"],
            job["company"],
            job["location"],
            job["source"],
            job["url"],
        ]
        for job in jobs
        if job["url"] not in existing_urls
    ]

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")

    print(f"Google Sheet updated: {len(new_rows)} new job(s) added.")


if __name__ == "__main__":
    main()
