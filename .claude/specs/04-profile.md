# Spec: Step 4 — Profile Page (Hardcoded UI)

## Overview

This step replaces the `/profile` stub with a fully designed profile page that displays static, hardcoded data. The goal is to establish the complete UI layout and visual design before any real database queries are wired up in Step 05. Four sections are built: a user info card, a summary stats row, a transaction history table, and a category breakdown. Building the UI first lets the team validate the design in isolation and ensures the templates are ready before the backend-connection step — no debugging layout and data-fetching logic at the same time.

---

## Depends On

- Step 01 — Database Setup: schema must exist
- Step 02 — Registration: user accounts must be creatable
- Step 03 — Login + Logout: `session["user_id"]` must be set; `/profile` must be a protected route that redirects unauthenticated users

---

## Routes

- `GET /profile`
  - Renders the profile page
  - Logged-in only — if `session.get("user_id")` is absent, redirect to `url_for("login")`
  - Already exists as a stub in `app.py`; this step upgrades it in place

---

## Database Changes

- No database changes
- The existing `users` and `expenses` tables are sufficient for future steps
- No DB queries in this step — all data displayed on the page is hardcoded in `app.py`

---

## Templates

Create `templates/profile.html` — a full profile page extending `base.html`. Must contain four sections:

1. **User info card** — avatar initials derived from name, full name, email address, and member-since date; all values hardcoded (e.g. name: `Demo User`, email: `demo@spendly.com`, member since: `June 2026`)

2. **Summary stats row** — a row of at least three stat tiles showing total amount spent, number of transactions, and top spending category; all values hardcoded (e.g. ₹18,240 spent, 34 transactions, top category: Food)

3. **Transaction history table** — a table of recent expenses with columns for date, description, category badge, and amount; at least three hardcoded rows spanning different categories and dates

4. **Category breakdown** — per-category spending displayed as a list or progress-bar rows with a label, a visual bar, and a total amount; at least three hardcoded categories

---

## Files to Change

- `app.py`
  - Replace the `/profile` stub with a real view function that:
    - Checks `session.get("user_id")`; if absent, redirects to `url_for("login")`
    - Constructs hardcoded context variables — a `user` dict, a `stats` dict, an `expenses` list of dicts, and a `categories` list of dicts
    - Passes all context variables to `render_template("profile.html", ...)`

---

## Files to Create

- `templates/profile.html`

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()` if any DB call is ever needed in a later step
- Parameterised queries only — never use string formatting in SQL (applies to any future queries added to this file)
- Authentication guard: check `session.get("user_id")`; if absent, `redirect(url_for("login"))`
- All data passed to the template must be hardcoded Python dicts and lists in `app.py` — no DB queries in this step
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- No inline `style` attributes anywhere in `profile.html`
- All templates must extend `base.html`
- Category badges must use a CSS class for their colour — not inline colour styles
- Use `url_for()` for every internal link — never hardcode paths

---

## Definition of Done

- [ ] Visiting `/profile` without being logged in redirects to `/login`
- [ ] Visiting `/profile` while logged in returns HTTP 200
- [ ] The page displays a user info card with a name and email
- [ ] The page displays at least three summary stat values (total spent, transaction count, top category)
- [ ] The page displays a transaction history table with at least three hardcoded rows
- [ ] The page displays a category breakdown section with at least three categories
- [ ] The navbar shows the logged-in state (username and logout link)
- [ ] No hex colour values appear in `profile.html` — only CSS custom properties
