from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created_at.strftime("%B %Y"),
    }


def get_summary_stats(user_id):
    conn = get_db()
    totals = conn.execute(
        "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    top_row = conn.execute(
        "SELECT category FROM expenses WHERE user_id = ?"
        " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return {
        "total_spent": float(totals[0]),
        "transaction_count": int(totals[1]),
        "top_category": top_row["category"] if top_row else "—",
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses"
        " WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS amount FROM expenses"
        " WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    if not rows:
        return []

    data = [{"name": row["category"], "amount": row["amount"]} for row in rows]
    total = sum(d["amount"] for d in data)

    raw_pcts = [(d["amount"] / total) * 100 for d in data]
    floors = [int(p) for p in raw_pcts]
    remainders = [raw_pcts[i] - floors[i] for i in range(len(floors))]

    deficit = 100 - sum(floors)
    indices_by_remainder = sorted(range(len(remainders)), key=lambda i: remainders[i], reverse=True)
    for i in range(deficit):
        floors[indices_by_remainder[i]] += 1

    for i, d in enumerate(data):
        d["pct"] = floors[i]

    return data
