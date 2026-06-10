# Claude Response

I have everything I need. The change is isolated to one file; the other affected files (export routes, reporting modules) aren't involved in this UI-text change.

## Implementation Plan: Russian helper text on Reports page

### Goal
Add a small Russian helper sentence under the Reports page title explaining that generated reports can be reviewed and exported there.

### Established pattern
The previous commit `812e356` ("Add RSS sources helper text") set the convention: a second `<p>` directly under the existing subtitle, styled `mt-1 text-xs text-slate-400`, containing a short Russian sentence. I'll mirror it exactly for consistency.

### The single change — `app/reports/page.tsx`

Current header block (lines 54–59):
```tsx
<div>
  <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
  <p className="mt-1 text-sm text-slate-500">
    Saved analyses — open without re-running Claude.
  </p>
</div>
```

Add a new `<p>` after the existing subtitle (leaving the English subtitle untouched, exactly as the sources commit left its primary subtitle in place):
```tsx
<div>
  <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
  <p className="mt-1 text-sm text-slate-500">
    Saved analyses — open without re-running Claude.
  </p>
  <p className="mt-1 text-xs text-slate-400">
    Здесь можно просматривать и экспортировать сформированные отчёты.
  </p>
</div>
```

The Russian text means "Here you can review and export generated reports" — matching the requested wording (review + export).

### Why no other affected files change
The other listed files are export/report-generation backend (`app/api/report/[id]/*`, `lib/export/*`, `src/report*.ts`, `src/reporting/*`, `src/importers/*`). They handle producing/exporting report data and have no bearing on a static UI helper string. No changes needed there.

### Scope & safety
- One additive JSX line; no logic, props, state, or imports touched.
- Reversible by deleting the added `<p>`.
- No auth/billing/secrets/schema/deploy impact.

### Verification
- `npm run dev` (or the project's dev command) → open `/reports` → confirm the grey helper line appears beneath the subtitle and renders the Cyrillic correctly.

### One note (not a blocker)
The existing Reports subtitle is still in English while the sources page is fully Russian. The request only asks to *add* a Russian helper, so I'm leaving the English subtitle as-is (consistent with how commit `812e356` left the sources subtitle). If you'd prefer the whole header translated to Russian, say so and I'll fold that in.

Plan only — no files modified.

