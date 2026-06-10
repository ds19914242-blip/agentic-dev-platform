### Task 001 — Translate document metadata in layout

**Goal:** Make the browser/document title and meta description Russian.
**Scope:** Translate the `metadata.title` and `metadata.description` in the root layout; confirm `lang="ru"` and Cyrillic font subset remain intact. No structural changes.
**Suggested files:** `app/layout.tsx`
**Acceptance criteria:** Page title and meta description render in Russian; `<html lang="ru">` unchanged; build/typecheck passes.
**Risk:** low
