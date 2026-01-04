# templates/

## Purpose

The `templates` folder contains all **HTML templates** used by KittyLit.
These templates define the **structure of the UI pages** and delegate all logic to backend routes (`app/`) and frontend assets (`static/`).

Templates are kept deliberately simple and readable.

---

## Files Overview

### `index.html`

Main user-facing page for KittyLit.

Responsibilities:
- Render the book recommendation form
- Collect user-selected filters (age, genre, language, year_category)
- Display recommendation results in a structured table
- Show a clear query summary for transparency
- Provide access to the Developer Logs page

Key design choices:
- Uses `year_category` instead of exact publication year for stability
- Avoids displaying ISBN to reduce UI clutter
- Keeps JavaScript inline and minimal
- Delegates styling to `static/css/warmstyle.css`

This template does **not** contain business logic or recommendation rules.

---

### `developer_logs.html`

Developer-focused monitoring and observability page.

Responsibilities:
- Display structured system logs in a readable format
- Auto-refresh logs periodically
- Allow downloading logs as a JSON file
- Support debugging and audit review

Key design choices:
- Clean, minimal layout
- Developer-first readability
- No styling dependencies on main UI theme
- Uses frontend fetch calls to `/developer/logs`

This page exists strictly for **debugging, governance, and transparency**.

---

## What This Folder Does NOT Do

- No data processing
- No validation logic
- No recommendation logic
- No API orchestration
- No styling logic

All logic lives in backend modules and static assets.

---

## Design Philosophy

- Minimal HTML
- Clear separation of concerns
- Templates describe structure, not behavior
- Debugging and user experience are intentionally separated

The `templates` folder exists to **present information clearly**, not to decide it.
