# Spec: Step 3 — Login and Logout

## Overview

This step converts the `/login` stub into a functional `POST` handler that verifies user credentials against the `users` table, stores the authenticated user's `id` in `session["user_id"]`, and redirects to the landing page (until a dedicated dashboard route exists). It also implements `/logout`, which clears the session entirely and redirects to `/`. After this step the app can distinguish logged-in users from guests at the session level. This is a prerequisite for all expense features — every protected route in later steps will check for `session["user_id"]`.

---

## Depends On

- Step 01 — Database Setup: the `users` table must exist and `get_db()` must be available
- Step 02 — Registration: `create_user()` and password hashing must be in place; at least one user (the seeded demo user) must exist in the database to log in against

---

## Routes

- `GET /login`
  - Renders the login form
  - Public — no authentication required
  - Already exists as a stub; this step upgrades it in place

- `POST /login`
  - Accepts form data: `email`, `password`
  - Looks up the user by email via `get_user_by_email()`
  - Verifies the submitted password against the stored hash
  - On success: sets `session["user_id"]` and redirects to `url_for("landing")`
  - On failure: flashes a generic error and re-renders the login form — no redirect
  - Public — no authentication required

- `GET /logout`
  - Calls `session.clear()`
  - Redirects to `url_for("landing")`
  - Public — no login required to hit this route

---

## Database Changes

- No new tables or columns
- The `users` table from Step 01 already stores `email` and `password_hash`
- One new helper function to add to `database/db.py`:
  - `get_user_by_email(email)`
    - Queries the `users` table for a row matching the given email
    - Returns the matching row (as a `sqlite3.Row`) or `None` if no match is found
    - Must live in `database/db.py` — not defined inline in the route function

---

## Templates

- Modify `templates/login.html`:
  - Add a `<form>` with `action="{{ url_for('login') }}"` and `method="post"`
  - Include `email` and `password` input fields with matching `name` attributes
  - Add a block to display flashed messages above the form — iterate over `get_flashed_messages()` and render each as a visible error element
  - Add a link to `/register` for users who do not yet have an account
  - Keep all existing visual design unchanged — do not modify layout, typography, or CSS classes

---

## Files to Change

- `app.py`
  - Upgrade `login()` to handle both `GET` and `POST`
  - Add credential verification, session assignment, flash messaging, and redirect logic
  - Implement `logout()` with `session.clear()` and redirect

- `database/db.py`
  - Add the `get_user_by_email(email)` helper function

- `templates/login.html`
  - Wire up form `action`, `method`, `name` attributes, flash message display, and registration link

---

## Files to Create

None.

---

## New Dependencies

None. Uses only:

- `werkzeug.security.check_password_hash` — already installed
- Flask builtins: `session`, `flash`, `redirect`, `url_for` — no new packages required

---

## Rules for Implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- All SQL must use `?` parameterised placeholders — never f-strings or string concatenation in SQL
- Verify passwords with `werkzeug.security.check_password_hash` — never compare plaintext
- The session key for the logged-in user must be `session["user_id"]` storing an integer — do not use any other key name or type
- Use `flask.session` — do not roll a custom session mechanism
- On any login failure (wrong password or unregistered email) flash exactly: `"Invalid email or password."` — do not reveal which field was incorrect
- After successful login redirect to `url_for("landing")` until a dashboard route exists
- `logout()` must call `session.clear()` then redirect to `url_for("landing")`
- All templates must extend `base.html`
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode paths

---

## Definition of Done

- [ ] `GET /login` renders the login form with `email` and `password` fields
- [ ] Submitting valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`
- [ ] Submitting a wrong password flashes `"Invalid email or password."` and re-renders the login form
- [ ] Submitting an unregistered email flashes the same generic error and re-renders the login form
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer present in the session
- [ ] The `/logout` route no longer returns the raw stub string
