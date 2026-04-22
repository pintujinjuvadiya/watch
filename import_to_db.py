import sqlite3
import gspread
from google.oauth2.service_account import Credentials

# 🔐 GOOGLE AUTH
scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "14jWhRGOWOXD3CpQkt1Dr3siokpCsIwxJTa7lJFDup1c"
sheet = client.open_by_key(SHEET_ID).sheet1

data = sheet.get_all_records()

# 🗄️ DB CONNECT
conn = sqlite3.connect("database.db")
c = conn.cursor()

print("🔄 Importing data into DB...")

for row in data:
    symbol = str(row.get("Symbol", "")).strip().upper()

    if not symbol:
        continue

    np1 = row.get("NP PY")
    np2 = row.get("NP 3Q")
    np3 = row.get("NP 2Q")
    np4 = row.get("NP Prev")
    np5 = row.get("NP Latest")

    yoy = row.get("YoY")
    p2p = row.get("P2P")
    pre_qoq = row.get("Pre QoQ")
    l_qoq = row.get("L QoQ")

    # check exists
    c.execute("SELECT symbol FROM watchlist WHERE symbol=?", (symbol,))
    exists = c.fetchone()

    if exists:
        # 🔁 UPDATE
        c.execute("""
            UPDATE watchlist SET
            np1=?, np2=?, np3=?, np4=?, np5=?,
            yoy=?, p2p=?, pre_qoq=?, l_qoq=?
            WHERE symbol=?
        """, (
            np1, np2, np3, np4, np5,
            yoy, p2p, pre_qoq, l_qoq,
            symbol
        ))
        print(f"🔁 Updated: {symbol}")

    else:
        # 🆕 INSERT
        c.execute("""
            INSERT INTO watchlist (
                symbol,
                np1, np2, np3, np4, np5,
                yoy, p2p, pre_qoq, l_qoq
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            np1, np2, np3, np4, np5,
            yoy, p2p, pre_qoq, l_qoq
        ))
        print(f"🆕 Inserted: {symbol}")

conn.commit()
conn.close()

print("✅ Import Complete")