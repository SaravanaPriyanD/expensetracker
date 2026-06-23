# Spec: Step 2 — User Registration

## Overview

This step upgrades the existing stub `GET /register` route into a fully functional registration flow that handles both `GET` and `POST`. The form accepts four fields: `name`, `email`, `password`, and `confirm_password`. On successful registration, the user is shown a success flash message and redirected to `/login`. This is the entry point for all authenticated features — no user can log in, view a profile, or track expenses until they have registered.

---

## Depends On

- Step 01 — Database setup: `users` table must exist, `get_db()` must be available from `database.db`

---

## Routes

- `GET /register`
  - Renders the registration form
  - Public — no authentication required
  - Already exists as a stub; this step upgrades it in place

- `POST /register`
  - Accepts form data: `name`, `email`, `password`, `confirm_password`
  - Validates input server-side (see Rules for Implementation)
  - On success: inserts a new user row, flashes a success message, redirects to `/login`
  - On failure: re-renders the form with a flashed error message — no redirect
  - Public — no authentication required

---

## Database Changes

- No new tables or columns
- The existing `users` table covers all requirements
- One new helper function to add to `database/db.py`:
  - `create_user(name, email, password)`
    - Hashes `password` using `generate_password_hash` from `werkzeug.security`
    - Inserts a new row into `users` with the provided `name`, `email`, and the resulting `password_hash`
    - Returns the `lastrowid` of the newly inserted user
    - Raises `sqlite3.IntegrityError` if the email is already taken (enforced by the UNIQUE constraint on `users.email`)

---

## Templates

- Modify `templates/register.html`:
  - Set the form `action` to `{{ url_for('register') }}` and `method="post"`
  - Ensure every input has the correct `name` attribute: `name`, `email`, `password`, `confirm_password`
  - Add a block to display flashed messages above the form — iterate over `get_flashed_messages()` and render each as a visible error element
  - Keep all existing visual design unchanged — do not modify layout, typography, or CSS classes

---

## Files to Change

- `app.py`
  - Set `app.secret_key` to a hardcoded dev string
  - Upgrade `register()` to handle both `GET` and `POST`
  - Add server-side validation, `create_user()` call, flash messaging, and redirect logic

- `database/db.py`
  - Add the `create_user(name, email, password)` helper function

- `templates/register.html`
  - Wire up `action`, `method`, `name` attributes, and flash message display

---

## Files to Create

None.

---

## New Dependencies

None. Uses only:

- `werkzeug.security` — already installed
- Flask builtins: `flash`, `redirect`, `url_for` — no new packages required

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only
- All SQL must use `?` parameterised placeholders — never f-strings or string concatenation in SQL
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext passwords
- `app.secret_key` must be set in `app.py` for `flash()` to work — a hardcoded dev string is acceptable for this step
- Server-side validation must run in this exact order:
  1. All four fields are non-empty — flash an error and re-render if any are blank
  2. `password` equals `confirm_password` — flash "Passwords do not match" and re-render if they differ
  3. Email is not already registered — call `create_user()` and catch `sqlite3.IntegrityError`; flash "Email already registered" and re-render on conflict
- On any validation failure: re-render the form with the flashed error — do not redirect
- On success: flash a success message and redirect to `url_for('login')`
- Use `abort(405)` if an unsupported HTTP method reaches the route
- All templates must extend `base.html`
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs

---

## Definition of Done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting all valid fields creates a new row in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error and makes no DB insert
- [ ] Submitting with an already-registered email re-renders with "Email already registered"
- [ ] Submitting with any empty field re-renders with a validation error
- [ ] The stored password is a hash — never plaintext — verifiable by inspecting `spendly.db`
- [ ] Submitting the same valid email a second time does not create a duplicate user
