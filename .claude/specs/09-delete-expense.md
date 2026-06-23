# Spec: Step 9 — Delete Expense

## Overview

Step 09 lets a logged-in user permanently delete one of their own expenses directly from the profile transaction table. A "Delete" button per row submits a `POST` request to `/expenses/<id>/delete`. The handler verifies ownership, removes the row from the database, and redirects back to `/profile`. There is no separate confirmation page — a browser-side `confirm()` dialog on the button's `onsubmit` handler is used to prevent accidental deletions. The existing `get_expense_by_id` helper from Step 08 is reused for ownership verification — no new query lookup functions are needed. Only one new mutation helper is added: `delete_expense` in `database/queries.py`.

---

## Depends On

- Step 01 — Database Setup: the `expenses` table must exist
- Step 03 — Login / Logout: `session["user_id"]` must be set and enforced
- Step 05 — Profile page renders the transaction list where the delete button lives
- Step 08 — Edit Expense: `get_expense_by_id` is available; the "Actions" column already exists in the profile transactions table

---

## Routes

- `POST /expenses/<int:id>/delete`
  - Verifies ownership, deletes the expense row, redirects to `/profile`
  - Logged-in only — redirect to `/login` if `session.get("user_id")` is absent

- No `GET` handler — a bare `GET` to this URL must return 405

---

## Database Changes

- No new tables or columns
- The `expenses` table already has all required columns

---

## Templates

- Modify `templates/profile.html`:
  - Inside the existing "Actions" cell per transaction row, add a delete form alongside the existing "Edit" link:
    - `<form>` with `method="POST"` and `action="{{ url_for('delete_expense', id=tx.id) }}"`
    - `style="display:inline"` on the `<form>` tag is the one permitted exception to the no-inline-styles rule — it is a layout-utility value only, not a design value
    - `onsubmit="return confirm('Delete this expense?')"` on the `<form>` tag to provide browser-side confirmation before submission
    - A `<button>` with `class="btn-delete"` and label `"Delete"`
  - The "Edit" link from Step 08 remains alongside the new "Delete" button

---

## Files to Change

- `database/queries.py`
  - Add `delete_expense(expense_id, user_id)`:
    - Issues a parameterised `DELETE FROM expenses WHERE id = ? AND user_id = ?`
    - The dual-column `WHERE` clause is the ownership guard
    - Commits and closes the connection before returning
    - Does not raise an error if 0 rows are deleted

- `app.py`
  - Import `delete_expense` from `database.queries`
  - Replace the `GET`-only placeholder at `/expenses/<int:id>/delete` with a `POST`-only handler:
    - Check `session.get("user_id")`; redirect to `url_for("login")` if absent
    - Call `get_expense_by_id(id, session["user_id"])`; `abort(404)` if result is `None`
    - Call `delete_expense(id, session["user_id"])`
    - Redirect to `url_for("profile")`
  - Route decorator: `@app.route("/expenses/<int:id>/delete", methods=["POST"])`

- `templates/profile.html`
  - Add the delete `<form>` inside the existing "Actions" cell per row

- `static/css/style.css`
  - Add a `.btn-delete` style using CSS variables for danger colour (e.g. `var(--danger)` or equivalent red-toned variable) — never hardcode hex values

---

## Files to Create

None.

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- All SQL must use `?` parameterised placeholders — never string-format values into SQL
- `PRAGMA foreign_keys = ON` must be active on every connection — already handled by `get_db()`
- `delete_expense` must scope its `DELETE` to `id = ? AND user_id = ?` — this is the ownership guard that prevents one user deleting another user's expense
- The route must only accept `POST` — a bare `GET` to the URL must return 405
- Unauthenticated access must redirect to `/login` (302)
- If the expense does not exist or belongs to another user, `abort(404)`
- After successful deletion, redirect to `url_for("profile")` — do not render a template
- The only permitted inline style is `style="display:inline"` on the `<form>` tag — no hex colours or design values may be inlined anywhere
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- All templates must extend `base.html`
- Currency must always display as `₹` — never `£` or `$`
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to Write

File: `tests/test_delete_expense.py`

### Unit tests

| Function | Input | Expected Output |
|---|---|---|
| `delete_expense` | valid `expense_id`, correct `user_id` | row removed from DB |
| `delete_expense` | valid `expense_id`, wrong `user_id` | row remains in DB; 0 rows deleted; no error raised |
| `delete_expense` | non-existent `expense_id` | no error raised; DB unchanged |

### Route tests

- `POST /expenses/<id>/delete` unauthenticated → redirects to `/login` (302)
- `POST /expenses/<id>/delete` authenticated, own expense → redirects to `/profile` (302); row no longer exists in the database
- `POST /expenses/<id>/delete` authenticated, another user's expense → returns 404; row still exists in the database
- `POST /expenses/<id>/delete` authenticated, non-existent `id` → returns 404
- `GET /expenses/<id>/delete` any user → returns 405 (Method Not Allowed)

---

## Definition of Done

- [ ] `POST /expenses/<id>/delete` while logged out redirects to `/login`
- [ ] `POST /expenses/<id>/delete` for a non-existent or another user's expense returns 404
- [ ] `GET /expenses/<id>/delete` returns 405
- [ ] Clicking "Delete" on a transaction row and confirming in the browser dialog removes that expense from the database
- [ ] After deletion, the user is redirected to `/profile` and the deleted expense no longer appears in the transaction list
- [ ] Cancelling the browser `confirm()` dialog does not submit the form and leaves the expense intact
- [ ] Each transaction row in the profile table now shows both "Edit" and "Delete" actions
