# static/css/

## Purpose

This folder contains all **CSS stylesheets and lightweight frontend scripts** used by KittyLit.
It is strictly a **presentation layer** and does not contain any business logic, data handling, or backend interaction.

The styling emphasizes:
- clarity
- calm, warm visual tone
- readability for parents and developers
- minimal distraction from content

---

## Files Overview

### `warmstyle.css`

Primary stylesheet for the **main KittyLit user interface**.

Responsibilities:
- Global layout and background styling
- Form styling for book search inputs
- Results table layout and hover effects
- Query summary presentation
- Chatbot button and panel styling
- Consistent typography and spacing

Design characteristics:
- Warm, friendly color palette
- Soft shadows and rounded corners
- Background image–based layout
- Minimal animations for usability, not decoration
- Accessibility-friendly contrasts

This file defines the **core visual identity** of the application.

---

### `developer_logs.css`

Dedicated stylesheet for the **Developer Logs page**.

Responsibilities:
- Clean, minimal layout for structured logs
- Readable typography for debugging
- Clear separation between log entries
- Neutral background for focus

Design characteristics:
- No decorative elements
- Developer-first readability
- Simple containers and spacing
- Designed to support JSON log inspection

This file intentionally avoids visual complexity.

---

## Subfolder: `js/`

Contains lightweight JavaScript used **only for frontend interaction**.

### `js/developer_logs.js`

Responsibilities:
- Fetch developer logs from backend endpoint
- Render logs dynamically in the UI
- Handle basic client-side interactions

No business rules or backend logic are implemented here.

---

## What This Folder Does NOT Do

- No API orchestration
- No data processing
- No validation logic
- No AI or recommendation logic
- No persistent state management

All logic lives in backend modules.

---

## Design Philosophy

- CSS-first layout
- Minimal JavaScript
- Clear separation between user UI and developer UI
- Calm visuals aligned with the domain (children & parents)
- Debugging views optimized for clarity, not aesthetics
