from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from services.sheet_service import get_sheet_data

app = Flask(__name__)


# 🔥 FETCH FULL DATA (ON ADD)
def fetch_and_update_stock(symbol):

    sheet_data = get_sheet_data()
    data = sheet_data.get(symbol)

    if not data:
        return False

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        UPDATE watchlist SET
            cmp=?, change=?,
            np1=?, np2=?, np3=?, np4=?, np5=?,
            yoy=?, p2p=?, pre_qoq=?, l_qoq=?
        WHERE symbol=?
    """, (
        data.get("cmp"),
        data.get("change"),
        data.get("np1"),
        data.get("np2"),
        data.get("np3"),
        data.get("np4"),
        data.get("np5"),
        data.get("yoy"),
        data.get("p2p"),
        data.get("pre_qoq"),
        data.get("l_qoq"),
        symbol
    ))

    conn.commit()
    conn.close()

    return True


# 🏠 MAIN DASHBOARD
@app.route("/")
def index():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    rows = c.execute("""
        SELECT id, symbol,
               np1, np2, np3, np4, np5,
               yoy, p2p, pre_qoq, l_qoq,
               bo_level, tag,
               cmp, change
        FROM watchlist
    """).fetchall()

    # 🔥 UPDATE FROM GOOGLE SHEET
    sheet_data = get_sheet_data()

    for row in rows:
        symbol = row[1]
        data = sheet_data.get(symbol)

        if data:
            c.execute("""
                UPDATE watchlist
                SET cmp=?, change=?
                WHERE symbol=?
            """, (
                data.get("cmp"),
                data.get("change"),
                symbol
            ))

    conn.commit()
    conn.close()

    # 🔄 RELOAD UPDATED DATA
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    rows = c.execute("""
        SELECT id, symbol,
               np1, np2, np3, np4, np5,
               yoy, p2p, pre_qoq, l_qoq,
               bo_level, tag,
               cmp, change
        FROM watchlist
    """).fetchall()

    conn.close()

    stocks = []

    for row in rows:
        (
            id,
            symbol,
            np1, np2, np3, np4, np5,
            yoy, p2p, pre_qoq, l_qoq,
            bo_level, tag,
            cmp, change
        ) = row

        # 🔥 STRONG CMP CLEANING
        cmp_val = None

        if cmp not in (None, "", "-", "0", 0):
            try:
                cmp_val = float(cmp)
            except:
                cmp_val = None

        # 🔥 FINAL FILTER (THIS WAS MISSING PROPERLY)
        if cmp_val is None or cmp_val == 0:
            continue

        # CHANGE
        try:
            change_val = float(str(change).replace('%', ''))
        except:
            change_val = 0

        # BO
        try:
            bo_val = float(bo_level) if bo_level else None
        except:
            bo_val = None

        # DOWN BO
        down_bo = None
        if cmp_val and bo_val:
            down_bo = round(((cmp_val - bo_val) / cmp_val) * 100, 2)

        stocks.append({
            "symbol": symbol,

            "np1": np1,
            "np2": np2,
            "np3": np3,
            "np4": np4,
            "np5": np5,

            "yoy": yoy,
            "p2p": p2p,
            "pre_qoq": pre_qoq,
            "l_qoq": l_qoq,

            "bo": bo_level,
            "tag": tag,

            "cmp": cmp_val,
            "change": change_val,

            "down_bo": down_bo
        })

    return render_template("index.html", stocks=stocks)


# ➕ ADD STOCK
@app.route("/add", methods=["POST"])
def add_stock():

    symbol = request.form.get("symbol", "").upper().strip()

    if not symbol:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    exists = c.execute(
        "SELECT id FROM watchlist WHERE symbol=?",
        (symbol,)
    ).fetchone()

    if not exists:
        c.execute("""
            INSERT INTO watchlist (symbol)
            VALUES (?)
        """, (symbol,))
        conn.commit()

        fetch_and_update_stock(symbol)

    conn.close()

    return redirect("/")


# 🔄 UPDATE BO / TAG
@app.route("/update", methods=["POST"])
def update():
    data = request.get_json()

    symbol = data.get("symbol")
    bo = data.get("bo_level")
    tag = data.get("tag")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if bo is not None:
        c.execute("UPDATE watchlist SET bo_level=? WHERE symbol=?", (bo, symbol))

    if tag is not None:
        c.execute("UPDATE watchlist SET tag=? WHERE symbol=?", (tag, symbol))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


# ❌ DELETE
@app.route("/delete/<symbol>")
def delete(symbol):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM watchlist WHERE symbol=?", (symbol,))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)