# Spec: Step 1 — Database Setup

## 1. Overview

This step replaces the stub functions in `database/db.py` with a working SQLite implementation. It is the foundational step because every subsequent feature — user authentication, profile management, and expense tracking — depends on the database being initialised and accessible before any route is served.

Without this step, no data can be stored or retrieved. All future steps assume `get_db()`, `init_db()`, and `seed_db()` exist and behave as defined here.

---

## 2. Depends On

None. This is the first implementation step and has no prerequisites.

---

## 3. Routes

No new routes are introduced in this step. All existing placeholder routes in `app.py` remain unchanged and continue to return their current stub strings.

---

## 4. Database Schema

### Table A: `users`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `email` | TEXT | NOT NULL, UNIQUE |
| `password_hash` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

### Table B: `expenses`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → users(id) |
| `amount` | REAL | NOT NULL |
| `category` | TEXT | NOT NULL |
| `date` | TEXT | NOT NULL — must be in YYYY-MM-DD format |
| `description` | TEXT | — |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

---

## 5. Functions to Implement (`database/db.py`)

### `get_db()`
- Opens (or creates) `spendly.db` in the project root
- Sets `connection.row_factory = sqlite3.Row` so columns are accessible by name
- Executes `PRAGMA foreign_keys = ON` on every new connection
- Returns the connection object

### `init_db()`
- Creates both `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS`
- Safe to call multiple times — must not error or duplicate tables on repeated calls
- Uses `get_db()` internally

### `seed_db()`
- Checks whether the `users` table already contains any rows
- If rows exist, returns immediately without inserting anything (idempotent)
- If the table is empty, inserts:
  - One demo user: name `Demo User`, email `demo@spendly.com`, password `demo123` hashed with `generate_password_hash` from `werkzeug.security`
  - 8 sample expenses linked to that demo user's `id`, covering all 7 categories (Food, Transport, Bills, Health, Entertainment, Shopping, Other — one category gets a second entry), with dates spread across the current calendar month

---

## 6. Changes to `app.py`

- Import `get_db`, `init_db`, and `seed_db` from `database.db`
- On startup, call `init_db()` followed by `seed_db()` inside an `app.app_context()` block — this ensures the application context is active when the database is first touched
- The database must be fully initialised before the first request is served

Example startup block placement (inside `if __name__ == "__main__":` is not sufficient — use `with app.app_context()` at module level after `app` is defined):

```
with app.app_context():
    init_db()
    seed_db()
```

---

## 7. Files to Change

- `database/db.py` — replace stub bodies with full implementation
- `app.py` — add imports and startup initialisation block

---

## 8. Files to Create

None.

---

## 9. Dependencies

No new packages. Use only:

- `sqlite3` — Python standard library
- `werkzeug.security` — already installed via `requirements.txt`

---

## 10. Categories (Fixed List)

The only valid category values for expenses are:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

---

## 11. Rules for Implementation

- No ORM, no SQLAlchemy — raw `sqlite3` only
- All SQL must use parameterized queries (`?` placeholders) — never f-strings or string concatenation in SQL
- `PRAGMA foreign_keys = ON` must be executed on every connection returned by `get_db()`
- Store `amount` as `REAL`, not `INTEGER`
- Hash all passwords with `generate_password_hash` from `werkzeug.security` — never store plaintext
- `seed_db()` must be idempotent: calling it multiple times must produce no duplicate rows
- All date values must be stored as strings in `YYYY-MM-DD` format

---

## 12. Expected Behavior

### `get_db()`
- Returns a live `sqlite3.Connection` with `row_factory = sqlite3.Row`
- Foreign key enforcement is active on the returned connection
- Creates `spendly.db` in the project root if it does not exist

### `init_db()`
- Creates `users` and `expenses` tables on first call
- Subsequent calls complete without error and leave the schema unchanged

### `seed_db()`
- On first call: inserts the demo user and 8 expenses; database contains exactly those rows
- On repeated calls: detects existing rows and returns without inserting anything
- Database-level constraints enforced: NOT NULL, UNIQUE on email, FOREIGN KEY on `expenses.user_id`

---

## 13. Error Handling Expectations

- **Duplicate email insert** → SQLite raises `UNIQUE constraint failed: users.email`; the exception must propagate unmasked so callers can handle it
- **Expense with invalid `user_id`** → SQLite raises `FOREIGN KEY constraint failed` (requires `PRAGMA foreign_keys = ON` to be active)
- **Invalid or malformed queries** → exceptions bubble up as `sqlite3.OperationalError` or `sqlite3.ProgrammingError`; do not catch and suppress them — let them surface for debugging

No custom error-handling wrappers are required in this step.

---

## 14. Definition of Done

- [ ] `spendly.db` is created in the project root on app startup
- [ ] Both `users` and `expenses` tables exist with the correct schema and constraints
- [ ] Demo user `demo@spendly.com` exists with a properly hashed password
- [ ] Exactly 8 sample expenses exist, covering all 7 categories
- [ ] Running the app a second time produces no duplicate seed data
- [ ] `uv run app.py` starts without errors
- [ ] Inserting an expense with an invalid `user_id` raises a foreign key constraint failure
- [ ] All SQL in `database/db.py` uses `?` parameterized placeholders — no string formatting
