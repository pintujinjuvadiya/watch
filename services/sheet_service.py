import gspread
from google.oauth2.service_account import Credentials
import time
import os
import json

CACHE = {
    "data": {},
    "last_update": 0
}

CACHE_TTL = 10


def get_sheet_data():

    if time.time() - CACHE["last_update"] < CACHE_TTL:
        return CACHE["data"]

    scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # 🔥 ENV से credentials लेना (SAFE VERSION)
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise Exception("❌ GOOGLE_CREDENTIALS not found in environment")

    try:
        creds_dict = json.loads(creds_json)
    except Exception as e:
        raise Exception(f"❌ Invalid JSON in GOOGLE_CREDENTIALS: {e}")

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

    client = gspread.authorize(creds)

    sheet = client.open_by_key("14jWhRGOWOXD3CpQkt1Dr3siokpCsIwxJTa7lJFDup1c").sheet1
    rows = sheet.get_all_records()

    data = {}

    for row in rows:
        symbol = row.get("Symbol")

        data[symbol] = {
            "cmp": row.get("CMP"),
            "change": row.get("% Change"),

            "np1": row.get("NP PY"),
            "np2": row.get("NP 3Q"),
            "np3": row.get("NP 2Q"),
            "np4": row.get("NP Prev"),
            "np5": row.get("NP Latest"),

            "yoy": row.get("YoY"),
            "p2p": row.get("P2P"),
            "pre_qoq": row.get("Pre QoQ"),
            "l_qoq": row.get("L QoQ"),
        }

    CACHE["data"] = data
    CACHE["last_update"] = time.time()

    return data