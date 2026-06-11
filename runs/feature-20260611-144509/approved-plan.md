# Approved Plan

I have everything I need. The convention is clear from prior commits: translate only visible UI text to Russian, leaving code structure, classNames, and technical terms (Claude, PDF, RSS, TOP-N) intact.

## Implementation Plan — Task 003: Translate Hero component

### Scope
Translate the user-facing English text in **`components/Hero.tsx`** to Russian, matching the established convention from Tasks 001/002 (NavBar, reports page). This is the smallest safe change: a single file, text-only, fully reversible.

**Out of scope (and why):** Although the feature request lists many files, the task title is explicit — *Translate Hero component*. The other listed files contain no Hero text:
- `components/SourcePicker.tsx` — a separate component with its own button labels ("Upload TXT file", "RSS Collection"). Not part of the Hero; belongs to a different task. Leave untouched.
- `app/api/**/route.ts` — backend API handlers. No visible UI hero text; touching them risks auth/health/billing logic the rules forbid changing. Leave untouched.

If translating SourcePicker or API-layer strings is actually intended, that's a separate task and I'd want confirmation before expanding scope.

### The only file to change: `components/Hero.tsx`

Three text nodes get translated; everything else (JSX structure, `<br/>`, all `className` values, the `gradient-text` span split) stays identical.

| Line | English | Russian |
|------|---------|---------|
| 4 (`eyebrow`) | `Intelligence Platform` | `Платформа аналитики` |
| 6 (h1, line 1) | `Turn raw feeds into` | `Превратите сырые ленты в` |
| 8 (`gradient-text`) | `market intelligence` | `рыночную аналитику` |
| 11–12 (`p`) | `Upload a news export, pick your themes, and get a cited TOP-N briefing with trends, signals, and analysis — in minutes.` | `Загрузите экспорт новостей, выберите темы и получите аналитическую сводку TOP-N со ссылками, трендами, сигналами и анализом — за считанные минуты.` |

Notes:
- The `<br/>` split between line 1 and the `gradient-text` span is preserved; the Russian split ("Превратите сырые ленты в" / "рыночную аналитику") reads naturally and keeps the highlighted phrase intact.
- "TOP-N" kept as-is (technical term, consistent with how "Claude"/"PDF"/"RSS" were preserved in prior commits).
- Em dash `—` preserved.

### Verification
- Confirm the file still compiles/type-checks (text-only change in static JSX — no type impact).
- Visually: eyebrow, headline (with gradient highlight), and subtitle render in Russian.

### Commit
Single commit, following the prior naming pattern:
`Epic task: Task 003 — Translate Hero component`

---

This plan modifies **one file, text-only**. No auth, billing, secrets, schema, or deploy config touched. Ready to implement on approval.

