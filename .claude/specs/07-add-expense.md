# Spec: Step 7 — Add Expense

## Overview

Step 07 lets a logged-in user submit a new expense through a dedicated form page at `/expenses/add`. The route already exists as a `GET` placeholder; this step upgrades it to a full `GET + POST` handler. Validated data is inserted into the `expenses` table and the user is redirected back to the profile page on success. A reusable `insert_expense()` query helper is added to `database/queries.py`. An "Add Expense" button is added to `profile.html` and a nav link is added to `base.html` so users can navigate to the form from anywhere in the app.

---

## Depends On

- Step 01 — Database Setup: the `expenses` table must exist with all required columns
- Step 03 — Login / Logout: `session["user_id"]` must be set and checked for protected access
- Step 04 / 05 — Profile page must exist and be live — it is the natural redirect target after a successful save

---

## Routes

- `GET /expenses/add`
  - Renders the add-expense form
  - Logged-in only — redirect to `/login` if `session.get("user_id")` is absent

- `POST /expenses/add`
  - Reads and validates submitted form fields
  - Inserts a new expense row via `insert_expense()`
  - On success: redirects to `url_for("profile")`
  - On failure: re-renders the form with an error message and previously submitted values pre-filled
  - Logged-in only — redirect to `/login` if `session.get("user_id")` is absent

---

## Database Changes

- No database changes
- The `expenses` table already has all required columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`

---

## Templates

- Create `templates/add_expense.html`:
  - Extends `base.html`
  - `<form>` with `method="POST"` and `action="{{ url_for('add_expense') }}"`
  - Fields:
    - `amount` — `<input type="number">` with `step="0.01"`, `min="0.01"`, `required`
    - `category` — `<select>` with exactly 7 fixed options: `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`
    - `date` — `<input type="date">`, `required`, defaults to today's date
    - `description` — `<input type="text">`, optional, `maxlength="200"`
  - Submit button labelled `"Save Expense"` and a cancel link back to `/profile`
  - Flash/error message block displayed above the form
  - Previously submitted field values must be pre-populated on re-render after a validation failure

- Modify `templates/profile.html`:
  - Add an "Add Expense" button or link pointing to `url_for("add_expense")`, positioned near the transaction table heading

- Modify `templates/base.html`:
  - Add an "Add Expense" link in the navbar, visible only when `session.user_id` is set

---

## Files to Change

- `app.py`
  - Replace the `GET`-only placeholder at `/expenses/add` with a `GET + POST` handler:
    - Both methods: check `session.get("user_id")`; redirect to `url_for("login")` if absent
    - `GET`: render `add_expense.html`
    - `POST`: read form fields, run validation, call `insert_expense()`, redirect to `url_for("profile")` on success; re-render with errors on failure

- `database/queries.py`
  - Add `insert_expense(user_id, amount, category, date, description)`

- `templates/profile.html`
  - Add "Add Expense" button linking to `url_for("add_expense")`

- `templates/base.html`
  - Add "Add Expense" navbar link for logged-in users

---

## Files to Create

- `templates/add_expense.html`

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- All SQL must use `?` parameterised placeholders — never string-format values into SQL
- `PRAGMA foreign_keys = ON` must be active on every connection — already handled by `get_db()`
- Unauthenticated access to both `GET` and `POST /expenses/add` must redirect to `/login`
- Validation rules for `POST`, checked in this order:
  1. `amount`: required; must be a positive float greater than `0`; parse with `float()`, catch `ValueError`
  2. `category`: required; must be one of the 7 fixed categories; reject anything else
  3. `date`: required; must be a valid `YYYY-MM-DD` date; parse with `datetime.strptime`
  4. `description`: optional; strip whitespace; store `None` if blank
- On any validation error, re-render the form with the error message and all previously submitted values pre-filled
- After a successful insert, redirect to `url_for("profile")` — do not re-render the form
- Currency must always display as `₹` — never `£` or `$`
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- No inline `style` attributes in any template
- All templates must extend `base.html`
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to Write

File: `tests/test_add_expense.py`

### Unit tests

| Function | Input | Expected Output |
|---|---|---|
| `insert_expense` | valid `user_id`, `amount=50.0`, `category="Food"`, `date="2026-03-20"`, `description="Lunch"` | row inserted; querying the DB returns the new row with matching values |
| `insert_expense` | `description=None` | row inserted with `description` stored as `NULL` |

### Route tests

- `GET /expenses/add` unauthenticated → redirects to `/login` (302)
- `GET /expenses/add` authenticated → returns 200; response contains a `<select>` with all 7 category options; response contains a `<form>` with `method="post"`
- `POST /expenses/add` unauthenticated → redirects to `/login` (302)
- `POST /expenses/add` authenticated, valid data (`amount=50.0`, `category=Food`, `date=2026-03-20`, `description=Lunch`) → redirects to `/profile` (302); new expense row exists in the DB for the test user
- `POST /expenses/add` authenticated, missing `amount` → returns 200; response contains an error message
- `POST /expenses/add` authenticated, `amount=0` → returns 200; response contains an error message
- `POST /expenses/add` authenticated, non-numeric `amount` → returns 200; response contains an error message
- `POST /expenses/add` authenticated, invalid category (not in fixed list) → returns 200; response contains an error message
- `POST /expenses/add` authenticated, invalid date string → returns 200; response contains an error message
- `POST /expenses/add` authenticated, no `description` (optional field omitted) → redirects to `/profile` (302); row inserted with `description = NULL`

---

## Definition of Done

- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in shows a form with `amount`, `category`, `date`, and `description` fields
- [ ] The category dropdown contains exactly: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- [ ] Submitting a valid expense redirects to `/profile` and the new expense appears in the transaction list
- [ ] Submitting with a missing or zero `amount` re-renders the form with an error and previously entered values retained
- [ ] Submitting with an invalid category re-renders the form with an error
- [ ] Submitting with an invalid date re-renders the form with an error
- [ ] Submitting without a `description` saves the expense without error
- [ ] The "Add Expense" button on the profile page navigates to `/expenses/add`
- [ ] The navbar shows an "Add Expense" link when the user is logged in
