# Spec: Step 8 — Edit Expense

## Overview

Step 08 lets a logged-in user edit any of their own expenses via a pre-populated form at `/expenses/<id>/edit`. The `GET` handler loads the existing expense from the database and renders the form with its current values. The `POST` handler validates the submission and updates the row in place. Ownership is enforced: a user can only edit expenses that belong to them — any attempt to access another user's expense returns a 404. Two new query helpers are added to `database/queries.py`: `get_expense_by_id` and `update_expense`. The transactions table in `profile.html` gains an "Edit" action link per row, which requires `get_recent_transactions` to also return the expense `id`.

---

## Depends On

- Step 01 — Database Setup: the `expenses` table must exist with all required columns
- Step 03 — Login / Logout: `session["user_id"]` must be set and enforced
- Step 05 — Profile page renders the transaction list where the edit link lives
- Step 07 — Add Expense: establishes the form pattern and validation rules this step follows

---

## Routes

- `GET /expenses/<int:id>/edit`
  - Renders the edit form pre-populated with the existing expense's current values
  - Logged-in only — redirect to `/login` if `session.get("user_id")` is absent
  - Returns 404 if the expense does not exist or does not belong to the current user

- `POST /expenses/<int:id>/edit`
  - Validates submitted form fields and updates the expense row in place
  - Logged-in only — redirect to `/login` if `session.get("user_id")` is absent
  - Returns 404 if the expense does not exist or does not belong to the current user

---

## Database Changes

- No new tables or columns
- All required columns already exist in `expenses`: `id`, `user_id`, `amount`, `category`, `date`, `description`

---

## Templates

- Create `templates/edit_expense.html`:
  - Extends `base.html`
  - `<form>` with `method="POST"` and `action="{{ url_for('edit_expense', id=expense.id) }}"`
  - Fields (identical structure to `add_expense.html`, all pre-filled with current values):
    - `amount` — `<input type="number">` with `step="0.01"`, `min="0.01"`, `required`, pre-filled with current value
    - `category` — `<select>` with exactly 7 fixed options, pre-selected to the expense's current category
    - `date` — `<input type="date">`, `required`, pre-filled with current value
    - `description` — `<input type="text">`, optional, `maxlength="200"`, pre-filled with current value
  - Submit button labelled `"Save Changes"` and a cancel link back to `/profile`
  - Error message block displayed above the form on validation failure
  - On re-render after validation failure, the form must show the submitted values (not the original DB values)

- Modify `templates/profile.html`:
  - Add an `"Actions"` column header to the transactions table
  - Add an `"Edit"` link cell per row pointing to `url_for("edit_expense", id=tx.id)`

---

## Files to Change

- `database/queries.py`
  - Add `get_expense_by_id(expense_id, user_id)`:
    - Fetches a single expense row scoped to `id = ? AND user_id = ?`
    - Returns the row as a dict-like object, or `None` if not found or if the `user_id` does not match
  - Add `update_expense(expense_id, user_id, amount, category, date, description)`:
    - Issues a parameterised `UPDATE` scoped to `id = ? AND user_id = ?` as a second ownership guard
    - Does not raise an error if 0 rows are affected (ownership mismatch handled by the route layer)
  - Modify `get_recent_transactions`:
    - Add `id` to the `SELECT` column list so templates can build edit links

- `app.py`
  - Import `get_expense_by_id` and `update_expense` from `database.queries`
  - Replace the `GET`-only placeholder at `/expenses/<int:id>/edit` with a full `GET + POST` handler:
    - Both methods: check `session.get("user_id")`; redirect to `url_for("login")` if absent
    - `GET`: call `get_expense_by_id(id, user_id)`; `abort(404)` if result is `None`; render `edit_expense.html` with the expense and the categories list
    - `POST`: read form fields, validate (same rules as Step 07), call `update_expense()`, redirect to `url_for("profile")` on success; re-render with errors on failure
    - `abort(404)` on `POST` if `get_expense_by_id` returns `None` before attempting the update
  - Route decorator: `@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])`

- `templates/profile.html`
  - Add `"Actions"` column header to the transactions table
  - Add an `"Edit"` link cell per row

---

## Files to Create

- `templates/edit_expense.html`

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- All SQL must use `?` parameterised placeholders — never string-format values into SQL
- `PRAGMA foreign_keys = ON` must be active on every connection — already handled by `get_db()`
- `get_expense_by_id` must scope its query to `id = ? AND user_id = ?` — return `None` if not found or if ownership check fails
- `update_expense` must also include `user_id = ?` in its `WHERE` clause as a second ownership guard
- Unauthenticated access to both `GET` and `POST` must redirect to `/login`
- If the expense does not exist or belongs to another user, `abort(404)`
- Validation rules for `POST`, checked in this order:
  1. `amount`: required; must be a positive float greater than `0`; parse with `float()`, catch `ValueError`
  2. `category`: required; must be one of the 7 fixed categories; reject anything else
  3. `date`: required; must be a valid `YYYY-MM-DD` string; parse with `datetime.strptime`
  4. `description`: optional; strip whitespace; store `None` if blank
- On any validation error, re-render the form with the error message and the submitted (not original) values pre-filled
- After a successful update, redirect to `url_for("profile")` — do not re-render the form
- Currency must always display as `₹` — never `£` or `$`
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- No inline `style` attributes in any template
- All templates must extend `base.html`
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to Write

File: `tests/test_edit_expense.py`

### Unit tests

| Function | Input | Expected Output |
|---|---|---|
| `get_expense_by_id` | valid `expense_id`, correct `user_id` | returns the matching row as a dict-like object with correct field values |
| `get_expense_by_id` | valid `expense_id`, wrong `user_id` | returns `None` |
| `get_expense_by_id` | non-existent `expense_id` | returns `None` |
| `update_expense` | valid `expense_id`, correct `user_id`, new `amount=99.0` | row in DB reflects updated `amount`; other fields unchanged |
| `update_expense` | valid `expense_id`, wrong `user_id` | row in DB unchanged; no error raised |

### Route tests

- `GET /expenses/<id>/edit` unauthenticated → redirects to `/login` (302)
- `GET /expenses/<id>/edit` authenticated, own expense → returns 200; response contains form pre-filled with current values; correct category is pre-selected
- `GET /expenses/<id>/edit` authenticated, another user's expense → returns 404
- `GET /expenses/<id>/edit` authenticated, non-existent `id` → returns 404
- `POST /expenses/<id>/edit` unauthenticated → redirects to `/login` (302)
- `POST /expenses/<id>/edit` authenticated, valid data → redirects to `/profile` (302); updated values reflected in the database
- `POST /expenses/<id>/edit` authenticated, another user's expense → returns 404
- `POST /expenses/<id>/edit` authenticated, missing `amount` → returns 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, `amount=0` → returns 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, non-numeric `amount` → returns 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, invalid category → returns 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, invalid date string → returns 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, no `description` → redirects to `/profile` (302); row updated with `description = NULL`

---

## Definition of Done

- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`
- [ ] Visiting `/expenses/<id>/edit` for a non-existent or another user's expense returns 404
- [ ] Visiting `/expenses/<id>/edit` while logged in shows a form pre-filled with the expense's current values
- [ ] The category dropdown has the correct category pre-selected
- [ ] Submitting valid changes redirects to `/profile` and the updated values appear in the transaction list
- [ ] Submitting with a missing or zero `amount` re-renders the form with an error and the submitted values retained
- [ ] Submitting with an invalid category re-renders the form with an error
- [ ] Submitting with an invalid date re-renders the form with an error
- [ ] Submitting without a `description` saves the expense without error
- [ ] Each row in the profile transaction table has an "Edit" link pointing to the correct URL
