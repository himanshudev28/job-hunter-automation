import os
import json
import gspread
from google.oauth2.service_account import Credentials

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    os.environ["GOOGLE_SHEET_ID"]
).sheet1

sheet.append_row([
    "TEST",
    "GitHub Action",
    "Sheet Connected"
])

print("Google Sheet Updated Successfully")
