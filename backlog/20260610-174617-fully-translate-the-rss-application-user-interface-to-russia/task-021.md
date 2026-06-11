### Task 021 — Sweep for residual English UI strings

**Goal:** Final pass to catch any remaining hardcoded English UI strings missed by earlier tasks (e.g. ErrorState, ModeSelector, dynamic toast/error messages, ExportButtons descriptive text).
**Scope:** Grep across `app/**` and `components/**` for residual English visible strings; translate any found. Do not touch logs, identifiers, or non-UI strings.
**Suggested files:** `components/ErrorState.tsx`, `components/ModeSelector.tsx`, and any others surfaced by the sweep.
**Acceptance criteria:** A documented grep sweep shows no remaining visible English UI text; typecheck passes. Run last, after Tasks 001–020.
**Risk:** medium

---

**Sequencing notes:** Tasks 001–003 (shared, globally visible) first for immediate impact. Tasks 004–008 are fully-English standalone pages — fully parallelizable. Tasks 009–014 are shared report/display components. Tasks 015–020 finish partially-translated files (do after their related component tasks to avoid edit overlap). Task 021 is the closing sweep and should run last.

## Depends On

_None_
