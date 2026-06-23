# Spec: Step 5 — Backend Routes for Profile Page

## Overview

Step 05 replaces all hardcoded data in the `/profile` route with live queries against the SQLite database. The profile page currently renders a static demo user, fixed summary stats, a hand-typed transaction list, and a hardcoded category breakdown. This step wires those four sections to real data so every logged-in user sees their own expenses. Three parallel subagents handle the three independent data concerns — transaction history, summary stats, and category breakdown — before being integrated into the single `/profile` route.

---

## Depends On

- Step 01 — Database Setup: tables and `get_db()` must exist
- Step 02 — Registration: users must be stored in the database
- Step 03 — Login / Logout: `session["user_id"]` must be set on login
- Step 04 — Profile Page Static UI: `templates/profile.html` already renders all four sections with hardcoded data; the template structure is ready

---

## Routes

- No new routes
- The existing `GET /profile` route is modified in place — hardcoded context data is replaced with calls to query helpers

---

## Database Changes

- No database changes
- The `users` and `expenses` tables already have all required columns: `user_id`, `amount`, `category`, `date`, `description`, `created_at`

---

## Templates

- Modify `templates/profile.html`:
  - Confirm all currency values display the `₹` symbol — never `£` or `$`
  - All four dynamic sections (user info card, summary stats, transaction history, category breakdown) are already present in the template — no structural changes needed
  - Only the Jinja variables consumed by those sections change: they now receive real data instead of hardcoded values

---

## Files to Change

- `app.py`
  - Replace all hardcoded dicts and lists in the `profile()` view function with calls to the new helpers in `database/queries.py`
  - Pass the results directly to `render_template("profile.html", ...)`

- `templates/profile.html`
  - Confirm the `₹` symbol is used for all currency display; correct any instances of `£` or `$`

---

## Files to Create

- `database/queries.py`
  - Pure query helpers — no Flask imports
  - One function per data concern:
    - `get_user_by_id(user_id)` → dict with keys `name`, `email`, `member_since`; `member_since` formatted as `"Month YYYY"` (e.g. `"January 2026"`) derived from `users.created_at`; returns `None` if no matching user
    - `get_summary_stats(user_id)` → dict with keys `total_spent`, `transaction_count`, `top_category`; if the user has no expenses returns `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}`
    - `get_recent_transactions(user_id, limit=10)` → list of dicts, each with keys `date`, `description`, `category`, `amount`; ordered newest-first by `date`; returns empty list if no expenses
    - `get_category_breakdown(user_id)` → list of dicts, each with keys `name`, `amount`, `pct`; `pct` is the percentage of the user's total spending rounded to the nearest integer; `pct` values must sum exactly to 100 (apply rounding remainder adjustment to the largest category); ordered by `amount` descending; returns empty list if no expenses
  - Every function must call `get_db()` internally and close the connection before returning

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- All SQL must use `?` parameterised placeholders — never string-format values into SQL
- `PRAGMA foreign_keys = ON` must be active on every connection — already handled by `get_db()`
- Currency must always display as `₹` — never `£` or `$`
- `member_since` must be derived from `users.created_at` and formatted as `"Month YYYY"` (e.g. `"January 2026"`)
- `pct` values in category breakdown must sum to exactly 100; use integer rounding and adjust the largest-amount category to absorb any rounding remainder
- If a user has no expenses, all helpers must return zeros and empty collections — never raise exceptions for the empty case
- All helpers in `database/queries.py` must close the database connection before returning
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- No inline `style` attributes in any template
- All templates must extend `base.html`

---

## Tests to Write

File: `tests/test_backend_connection.py`

### Unit tests

| Function | Input | Expected Output |
|---|---|---|
| `get_user_by_id` | valid `user_id` | dict with correct `name`, `email`, `member_since` |
| `get_user_by_id` | non-existent `id` | `None` |
| `get_summary_stats` | `user_id` with expenses | correct `total_spent`, `transaction_count`, `top_category` |
| `get_summary_stats` | `user_id` with no expenses | `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` |
| `get_recent_transactions` | `user_id` with expenses | list ordered newest-first; each item has `date`, `description`, `category`, `amount` |
| `get_recent_transactions` | `user_id` with no expenses | empty list |
| `get_category_breakdown` | `user_id` with expenses | list ordered by `amount` desc; `pct` values are integers summing to 100 |
| `get_category_breakdown` | `user_id` with no expenses | empty list |

### Route tests

- `GET /profile` unauthenticated → redirects to `/login` (302)
- `GET /profile` authenticated as seed user:
  - returns HTTP 200
  - response body contains `"Demo User"`
  - response body contains `"demo@spendly.com"`
  - response body contains the `₹` symbol
  - `total_spent` displayed matches the sum of all seed expenses (`346.24`)
  - `transaction_count` displayed is `8`
  - `top_category` displayed is `"Bills"` (highest single-category total among seed data)
  - transaction list rows appear in newest-first order
  - category breakdown contains all 7 categories

---

## Definition of Done

- [ ] Logging in as `demo@spendly.com` / `demo123` shows `"Demo User"` and `"demo@spendly.com"` on the profile page — not hardcoded strings
- [ ] Total spent displayed on the profile page equals `₹346.24`
- [ ] Transaction count displayed is `8`
- [ ] Top category displayed is `"Bills"`
- [ ] Transaction list shows 8 rows ordered newest date first
- [ ] Category breakdown shows 7 categories with percentages that add up to 100%
- [ ] All amounts on the page display the `₹` symbol
- [ ] Registering a brand-new user and visiting `/profile` shows `₹0.00` total spent, `0` transactions, and an empty category breakdown — no errors
