# Spec: Step 6 — Date-Range Filter on Profile Page

## Overview

Step 06 adds a date-range filter to the existing `/profile` route so users can narrow the transaction list, summary stats, and category breakdown to a specific period. The filter is driven entirely by query-string parameters (`date_from` and `date_to`) on `GET /profile` — no new routes are required. A compact filter bar with four quick-select preset buttons ("This Month", "Last 3 Months", "Last 6 Months", "All Time") and two date input fields lets users pick any custom range. All three data sections (summary stats, recent transactions, category breakdown) must respect the active date filter.

---

## Depends On

- Step 01 — Database Setup: the `expenses` table with a `date` column (`TEXT`, `YYYY-MM-DD`) must exist
- Step 04 — Profile Page UI: `templates/profile.html` with all four sections must exist
- Step 05 — Backend Connection: `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` in `database/queries.py` must exist and be wired to the `/profile` route

---

## Routes

- No new routes
- The existing `GET /profile` route is modified to read two optional query parameters:
  - `date_from` — ISO date string `YYYY-MM-DD`, inclusive lower bound
  - `date_to` — ISO date string `YYYY-MM-DD`, inclusive upper bound
- If either parameter is absent or malformed, the route falls back to an unfiltered "All Time" view — it never errors out

---

## Database Changes

- No database changes
- The `expenses.date` column (`TEXT`, `YYYY-MM-DD`) already supports `BETWEEN` comparison in SQLite

---

## Templates

- Modify `templates/profile.html`:
  - Add a filter bar section above the summary stats row containing:
    - Four quick-select preset buttons: `"This Month"`, `"Last 3 Months"`, `"Last 6 Months"`, `"All Time"`
    - Each preset is a link to `/profile` with the appropriate `date_from` / `date_to` query params computed in `app.py` and passed to the template via context variables
    - `"All Time"` links to `/profile` with no query params (clean URL)
    - A custom-range sub-form with two `<input type="date">` fields (`date_from`, `date_to`) and an `"Apply"` submit button that `GET`s `/profile`
    - The currently active preset or custom range is visually highlighted with an active CSS state on the button
  - No structural changes to any existing section — only the Jinja variables fed into the stats, transaction, and category sections change when a filter is active

---

## Files to Change

- `app.py`
  - In `profile()`: read `date_from` and `date_to` from `request.args`
  - Validate each value with `datetime.strptime(value, "%Y-%m-%d")`; on `ValueError` treat the param as absent
  - If both params are present and valid but `date_from > date_to`: treat both as absent and flash `"Start date must be before end date."`
  - Compute all four preset date ranges in `app.py` (e.g. first day of the current month for "This Month") — never in the template
  - Pass `date_from`, `date_to`, and all preset URL strings back to the template so the filter bar can reflect the active state
  - Pass `date_from` and `date_to` as keyword arguments to each of the three query helpers

- `database/queries.py`
  - `get_summary_stats(user_id, date_from=None, date_to=None)`
    - When both params are provided: add `AND date BETWEEN ? AND ?` to the expenses queries
    - When both are absent: behave identically to the Step 05 implementation (unfiltered)
  - `get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)`
    - Same pattern; newest-first ordering and `limit` remain unchanged
  - `get_category_breakdown(user_id, date_from=None, date_to=None)`
    - Same pattern; percentage recalculation logic remains unchanged

- `templates/profile.html`
  - Add filter bar as described in the Templates section above

- `static/css/profile.css`
  - Add styles for the filter bar layout and the active-preset button state
  - Use CSS custom properties exclusively — never hardcode hex values

---

## Files to Create

None.

---

## New Dependencies

None.

---

## Rules for Implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- All SQL must use `?` parameterised placeholders — never string-format dates into SQL; use `?` placeholders even for date-range bounds
- Date validation in `app.py`: use `datetime.strptime(value, "%Y-%m-%d")`; on `ValueError` treat the param as absent and fall back to the unfiltered view
- Preset links must be generated with `url_for("profile", date_from=..., date_to=...)` — never hardcoded URL strings in the template
- When both `date_from` and `date_to` are absent, all three query helpers must behave identically to their Step 05 behaviour (unfiltered)
- If `date_from > date_to` after validation, treat both as absent and flash: `"Start date must be before end date."`
- The `"All Time"` preset must produce a clean `/profile` URL with no query params
- All preset date calculations must be computed in `app.py` — not in the template
- Use CSS custom properties (`var(--...)`) for all colour values — never hardcode hex values
- No inline `style` attributes in any template
- All templates must extend `base.html`
- Use `url_for()` for every internal link — never hardcode paths

---

## Definition of Done

- [ ] Visiting `/profile` with no query params returns the same data as Step 05 — unfiltered, all expenses
- [ ] Clicking "This Month" filters all three sections to the current calendar month only
- [ ] Clicking "Last 3 Months" filters to expenses in the 3-month window ending today
- [ ] Clicking "Last 6 Months" filters to expenses in the 6-month window ending today
- [ ] Clicking "All Time" removes any active filter and shows all expenses
- [ ] Submitting a custom date range with valid `date_from` and `date_to` shows only expenses within that range in all three sections
- [ ] Submitting a range where `date_from > date_to` shows a flash error and falls back to the unfiltered view
- [ ] Submitting a malformed date string (e.g. `date_from=not-a-date`) does not crash the app — it silently falls back to the unfiltered view
- [ ] The active preset button or custom-range fields visually indicate which filter is currently applied
- [ ] All amounts continue to display the `₹` symbol regardless of the active filter
- [ ] A user with no expenses in the selected range sees `₹0.00` total spent, `0` transactions, and an empty category breakdown — no errors
