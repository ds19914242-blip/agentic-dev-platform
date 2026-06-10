### Task 019 — Final English-string sweep across app/ and components/

**Goal:** Catch any remaining hardcoded English visible strings missed by per-file tasks (toasts, alert/confirm, aria-labels, placeholders, empty states).
**Scope:** Grep the `app/` and `components/` trees for residual user-facing English (e.g. quoted strings in JSX text, `placeholder=`, `aria-label=`, `alert(`, `confirm(`, `toast(`), translate what's user-visible, and leave brand/format/technical tokens. No new abstractions.
**Suggested files:** any file under `app/`, `components/` with residual English (verification-driven)
**Acceptance criteria:** A repo-wide search surfaces no remaining user-facing English UI strings (excluding agreed brand/format/technical tokens); typecheck/build passes.
**Risk:** medium
