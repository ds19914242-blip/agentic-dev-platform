# Epic

## Summary

Complete the Russian translation of the `rss-agent-lab_2` UI. The `<html lang>` is already `ru`, fonts include Cyrillic, and several surfaces (sources, reports, ConfirmModal, ErrorState, ProgressTimeline, UploadDropzone, TopicSelector, ModeSelector, BenchmarkTable) are already fully Russian. The remaining work is the home/analysis flow, dashboard, collections, feedback, reading-list, settings pages, finishing partial pages (login, profiles, benchmark, run/[id]), several English-only components (Hero, SourcePicker, Dashboard, SummaryCards, NewsCard, ExportButtons, NavBar nav links, Footer), and the page metadata title/description.

The codebase has **no i18n layer** — strings are hardcoded inline per component, and the existing Russian pages follow that same inline pattern. To stay consistent, low-risk, and independently shippable, each task translates strings inline in its own files rather than introducing a centralized strings module. Each task is one reviewable PR, scoped to a small set of files, and validates with `tsc`/build since no behavior changes.

## Assumptions

- We keep the existing inline-string approach (no new i18n framework), matching already-translated pages. Introducing a central strings module is explicitly out of scope to avoid a large, risky refactor.
- "User interface" = visible UI text: headings, labels, buttons, placeholders, empty states, toasts, alert/confirm dialogs, aria-labels, and document metadata. Backend/API messages, code comments, log output, and developer-only strings are out of scope unless they surface directly in the UI.
- Date/number formatting already uses `ru-RU` and needs no change.
- Brand/format tokens that are conventionally left as-is (e.g. "RSS", "Markdown", "JSON", "PDF", "DOCX", "LLM", product name "RSS Agent Lab") may remain untranslated; surrounding labels get translated.
- Redirect-only pages (`history`, `workspace`, `templates`, `rss/collections`) have no visible text and need no work.
- Russian wording should match the tone/terminology already used in translated pages (e.g. "Источники", "Отчёты", "Анализ").

## Task List

### Task 001 — Translate document metadata in layout

**Goal:** Make the browser/document title and meta description Russian.
**Scope:** Translate the `metadata.title` and `metadata.description` in the root layout; confirm `lang="ru"` and Cyrillic font subset remain intact. No structural changes.
**Suggested files:** `app/layout.tsx`
**Acceptance criteria:** Page title and meta description render in Russian; `<html lang="ru">` unchanged; build/typecheck passes.
**Risk:** low

### Task 002 — Translate NavBar navigation labels

**Goal:** Translate all navigation link labels and any remaining English chrome in the top navigation.
**Scope:** Translate nav item labels (dashboard, collections, sources, reports, feedback, reading-list, settings, profiles, benchmark, etc.) and any tooltips/aria-labels; the logout button ("Выйти") is already Russian — leave it.
**Suggested files:** `components/NavBar.tsx`
**Acceptance criteria:** Every visible nav label is Russian; routes/hrefs unchanged; active-state logic untouched; typecheck passes.
**Risk:** low

### Task 003 — Translate Hero component

**Goal:** Translate the marketing/intro copy on the landing hero.
**Scope:** Translate headline, subheadline, and any CTA text in the Hero component.
**Suggested files:** `components/Hero.tsx`
**Acceptance criteria:** All Hero visible text is Russian; layout/props unchanged; typecheck passes.
**Risk:** low

### Task 004 — Translate Footer

**Goal:** Translate footer labels while preserving app name/version tokens.
**Scope:** Translate any descriptive footer text/links; keep product name and version string format intact.
**Suggested files:** `components/Footer.tsx`, `lib/version.ts` (read-only if referenced)
**Acceptance criteria:** Footer visible text is Russian; version/build info still renders correctly; typecheck passes.
**Risk:** low

### Task 005 — Translate home/analysis page and SourcePicker

**Goal:** Finish the primary analysis flow (highest-volume English surface): hero buttons, upload/collection picker, labels, and any remaining English strings.
**Scope:** Translate visible text in the home page (button "Run Analysis →", "Choose a collection…", "Upload TXT file", "RSS Collection", labels, empty/help text) and the SourcePicker labels it uses. Existing Russian error strings remain.
**Suggested files:** `app/page.tsx`, `components/SourcePicker.tsx`
**Acceptance criteria:** All visible text on the home page and source picker is Russian; analysis-start behavior unchanged; typecheck passes.
**Risk:** medium

### Task 006 — Translate Dashboard page and Dashboard component

**Goal:** Translate the dashboard surface end to end.
**Scope:** Translate `app/dashboard/page.tsx` (title "Your intelligence dashboard", quick actions "Run Analysis"/"Add Source"/"Create Collection", section headers "Overview"/"Latest Reports"/"Recent Saved"/"Recent Activity", empty states) and the shared `components/Dashboard.tsx` (header "Intelligence Report" and remaining English labels).
**Suggested files:** `app/dashboard/page.tsx`, `components/Dashboard.tsx`
**Acceptance criteria:** All visible dashboard text is Russian (incl. empty states and section headers); data wiring unchanged; typecheck passes.
**Risk:** medium

### Task 007 — Translate SummaryCards component

**Goal:** Translate KPI/summary card labels used in reports/dashboard.
**Scope:** Translate "Collected", "Selected", "Potentially Relevant", "Trends" and any units/captions in SummaryCards.
**Suggested files:** `components/SummaryCards.tsx`
**Acceptance criteria:** All card labels are Russian; numeric/format logic unchanged; typecheck passes.
**Risk:** low

### Task 008 — Translate Collections page

**Goal:** Translate the collections management page.
**Scope:** Translate title "Collections", buttons ("Create collection", "Edit collection", "Add Source"), modal text, empty states, and any English toasts emitted from this page.
**Suggested files:** `app/collections/page.tsx`
**Acceptance criteria:** All visible text and toasts on the collections page are Russian; CRUD behavior unchanged; typecheck passes.
**Risk:** medium

### Task 009 — Translate Feedback page

**Goal:** Translate the feedback center.
**Scope:** Translate title "Feedback Center", vote labels ("Relevant", "Not Relevant", "Missed But Relevant"), KPI cards, section text, and empty states.
**Suggested files:** `app/feedback/page.tsx`
**Acceptance criteria:** All visible feedback page text is Russian; vote-submission logic and values unchanged; typecheck passes.
**Risk:** low

### Task 010 — Translate Reading List page

**Goal:** Translate the reading-list page.
**Scope:** Translate title "Reading List", action buttons ("Mark as Read", "Mark unread", "Remove", "Open Source"), filter options ("All", "Unread", "Read"), and empty states.
**Suggested files:** `app/reading-list/page.tsx`
**Acceptance criteria:** All visible reading-list text is Russian; filter and read/unread behavior unchanged; typecheck passes.
**Risk:** low

### Task 011 — Translate Settings page

**Goal:** Translate the settings page.
**Scope:** Translate title "Settings", option labels (feedback influence "Off"/"Low"/"Medium"/"High"), descriptions and help text.
**Suggested files:** `app/settings/page.tsx`
**Acceptance criteria:** All visible settings text is Russian; stored setting values/keys unchanged (translate display labels only, not persisted enum values); typecheck passes.
**Risk:** medium

### Task 012 — Finish Login page translation

**Goal:** Complete the partially translated login page.
**Scope:** Translate remaining English: "Sign In" button, the "admin" placeholder (translate placeholder text only, not any default credential value), and any other English fragments. Russian labels already present stay.
**Suggested files:** `app/login/page.tsx`
**Acceptance criteria:** Login page is fully Russian; auth submit behavior and field names unchanged; typecheck passes.
**Risk:** low

### Task 013 — Finish Profiles page translation

**Goal:** Complete the partially translated profiles page.
**Scope:** Translate remaining English form labels ("Include keywords", "Exclude keywords") and any English fragments; existing Russian title/toasts/modal stay. Ensure related aria-labels (e.g. `remove ${k}`) are Russian.
**Suggested files:** `app/profiles/page.tsx`
**Acceptance criteria:** Profiles page has no remaining English visible text; keyword data handling unchanged; typecheck passes.
**Risk:** low

### Task 014 — Finish Benchmark page translation

**Goal:** Complete the partially translated benchmark page.
**Scope:** Translate remaining English phase/status text and any English fragments; existing Russian title/buttons/confirm stay.
**Suggested files:** `app/benchmark/page.tsx`
**Acceptance criteria:** Benchmark page has no remaining English visible text; benchmark-run behavior unchanged; typecheck passes.
**Risk:** low

### Task 015 — Translate NewsCard component

**Goal:** Translate the article card UI.
**Scope:** Translate vote-mode labels, "save"/"saved" text, source/relevance labels, and any other English visible text in NewsCard.
**Suggested files:** `components/NewsCard.tsx`
**Acceptance criteria:** All NewsCard visible text is Russian; vote/save handlers and emitted values unchanged; typecheck passes.
**Risk:** low

### Task 016 — Translate ExportButtons labels and run/[id] page remnants

**Goal:** Translate the export control labels and finish the run detail page.
**Scope:** In ExportButtons, translate any descriptive text/aria-labels/tooltips while keeping format tokens ("Markdown", "JSON", "PDF", "DOCX"). In `app/run/[id]/page.tsx`, translate remaining English; existing Russian ("Отчёт не найден", "К истории") stays.
**Suggested files:** `components/ExportButtons.tsx`, `app/run/[id]/page.tsx`
**Acceptance criteria:** Export controls and run detail page have no remaining English visible text (format names may stay); download behavior unchanged; typecheck passes.
**Risk:** low

### Task 017 — Translate residual components (StatsPanel, TrendsPanel, StrategicSignals, ExecutiveSummary, ProgressView, PreviewPanel, ProfileSelector)

**Goal:** Sweep remaining shared report/analysis components for any English visible text.
**Scope:** Audit and translate any leftover English strings, labels, headings, and empty states in these components. Each is small; group as one PR. (PreviewPanel and ProfileSelector are partially Russian — finish them.)
**Suggested files:** `components/StatsPanel.tsx`, `components/TrendsPanel.tsx`, `components/StrategicSignals.tsx`, `components/ExecutiveSummary.tsx`, `components/ProgressView.tsx`, `components/PreviewPanel.tsx`, `components/ProfileSelector.tsx`
**Acceptance criteria:** None of these components render English visible text; data/props unchanged; typecheck passes.
**Risk:** medium

### Task 018 — Translate chart labels and axis/legend text

**Goal:** Translate user-facing labels in chart components.
**Scope:** Translate axis titles, legends, tooltips, and category labels in the chart components; keep numeric formatting.
**Suggested files:** `components/charts/CategoryChart.tsx`, `components/charts/ExclusionChart.tsx`, `components/charts/MatchedExcludedChart.tsx`, `components/charts/SourceChart.tsx`
**Acceptance criteria:** All chart-visible labels are Russian; chart data bindings unchanged; typecheck passes.
**Risk:** low

### Task 019 — Final English-string sweep across app/ and components/

**Goal:** Catch any remaining hardcoded English visible strings missed by per-file tasks (toasts, alert/confirm, aria-labels, placeholders, empty states).
**Scope:** Grep the `app/` and `components/` trees for residual user-facing English (e.g. quoted strings in JSX text, `placeholder=`, `aria-label=`, `alert(`, `confirm(`, `toast(`), translate what's user-visible, and leave brand/format/technical tokens. No new abstractions.
**Suggested files:** any file under `app/`, `components/` with residual English (verification-driven)
**Acceptance criteria:** A repo-wide search surfaces no remaining user-facing English UI strings (excluding agreed brand/format/technical tokens); typecheck/build passes.
**Risk:** medium
