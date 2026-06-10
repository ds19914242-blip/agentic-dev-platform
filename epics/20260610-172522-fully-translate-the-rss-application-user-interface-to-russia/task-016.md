### Task 016 — Translate ExportButtons labels and run/[id] page remnants

**Goal:** Translate the export control labels and finish the run detail page.
**Scope:** In ExportButtons, translate any descriptive text/aria-labels/tooltips while keeping format tokens ("Markdown", "JSON", "PDF", "DOCX"). In `app/run/[id]/page.tsx`, translate remaining English; existing Russian ("Отчёт не найден", "К истории") stays.
**Suggested files:** `components/ExportButtons.tsx`, `app/run/[id]/page.tsx`
**Acceptance criteria:** Export controls and run detail page have no remaining English visible text (format names may stay); download behavior unchanged; typecheck passes.
**Risk:** low
