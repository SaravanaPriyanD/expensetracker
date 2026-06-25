import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash


def get_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "spendly.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] > 0:
        conn.close()
        return

    pw_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", pw_hash),
    )
    user_id = cursor.lastrowid

    month = date.today().strftime("%Y-%m")
    expenses = [
        (user_id, 340.00, "Bills",        f"{month}-01", "Electricity bill"),
        (user_id,  85.50, "Food",          f"{month}-03", "Groceries"),
        (user_id,  45.00, "Transport",     f"{month}-05", "Fuel"),
        (user_id, 120.00, "Health",        f"{month}-08", "Pharmacy"),
        (user_id,  60.00, "Entertainment", f"{month}-10", "Movie tickets"),
        (user_id,  95.74, "Shopping",      f"{month}-12", "Clothing"),
        (user_id,  30.00, "Other",         f"{month}-15", "Miscellaneous"),
        (user_id,  65.00, "Food",          f"{month}-18", "Restaurant dinner"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()


def create_user(name, email, password):
    pw_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, pw_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id
