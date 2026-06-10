# Epic

## Translate the RSS application UI to Russian (inline text, no i18n framework)

## Summary

The app is partially translated. Several pages were already localized (`reports`, `run/[id]`, mostly `sources`, `profiles`, `login`, `benchmark`, home `page.tsx`), while others remain fully English (`dashboard`, `settings`, `reading-list`, `collections`, `feedback`). Shared components are a mix: some fully Russian, several fully English (`NavBar`, `Hero`, `SummaryCards`, `StrategicSignals`, `ExecutiveSummary`), and a few partially translated.

The work is decomposed page-by-page and component-by-component so each task is a small, independently shippable PR. Shared components (`NavBar` especially) are split out so they aren't translated redundantly across page tasks. Redirect-only pages (`history`, `rss`, `rss/collections`, `templates`, `workspace`) contain no UI text and are excluded. Charts and prop-driven components (`Toast`, `ConfirmModal`, `KpiCard`, `ExportButtons`, charts) carry no static UI text and are excluded except where they hardcode strings.

Each task can be validated with `tsc`/`next build` typecheck; there is no test suite. Tasks are ordered roughly: shared components first (visible everywhere), then fully-English pages, then "polish" tasks that finish partially-translated files.

## Assumptions

- Russian translation is for **visible UI text only**: labels, buttons, headings, placeholders, empty/error/toast states, helper text. Not data values, API responses, log messages, code identifiers, or analytics keys.
- Mode/format tokens that double as identifiers (`fast`/`balanced`/`deep`, `Markdown`/`JSON`/`PDF`/`DOCX`) stay as-is unless they are purely descriptive labels; translators should keep machine-meaningful values intact and only translate surrounding descriptive text.
- No i18n library, no extraction to message catalogs — strings stay inline in JSX/TSX, matching the existing pattern in already-translated files.
- Translation must not change component props, types, conditional logic, or string values used as map keys / state discriminators / API params.
- `app/layout.tsx` `metadata` (title/description) is user-visible (browser tab / SEO) and is in scope.
- Style/tone should match the already-translated pages (e.g. `reports`, `sources`) for consistency.
- Each task is safe to merge independently; partial completion of the epic leaves the app in a working bilingual state.

## Task List

### Task 001 — Translate NavBar navigation links

**Goal:** Translate all navigation link labels in the global nav bar to Russian.
**Scope:** Static link text and any aria-labels/titles; do not change route paths or hrefs.
**Suggested files:** `components/NavBar.tsx`
**Acceptance criteria:** All visible nav labels render in Russian; routes and active-state logic unchanged; typecheck passes. This is highest priority since NavBar appears on every page.
**Risk:** low

### Task 002 — Translate layout metadata and Footer

**Goal:** Translate the app `metadata` (title/description) and any static Footer text to Russian.
**Scope:** `metadata` object strings in layout; Footer static text (version number is dynamic — leave it).
**Suggested files:** `app/layout.tsx`, `components/Footer.tsx`
**Acceptance criteria:** Browser tab title/description in Russian; Footer static text (if any) in Russian; version rendering unchanged; typecheck passes.
**Risk:** low

### Task 003 — Translate Hero component

**Goal:** Translate the home-page Hero headline, subtext, and any CTA labels to Russian.
**Scope:** Static text in `components/Hero.tsx`.
**Suggested files:** `components/Hero.tsx`
**Acceptance criteria:** All Hero copy renders in Russian; props/structure unchanged; typecheck passes.
**Risk:** low

### Task 004 — Translate Dashboard page

**Goal:** Translate all user-facing English text on the dashboard page to Russian.
**Scope:** Headings, labels, links, empty/loading/error states in the dashboard page (not the reusable `Dashboard` component used for reports — see Task 013 for shared report components).
**Suggested files:** `app/dashboard/page.tsx`
**Acceptance criteria:** No English UI text remains on the dashboard page; data fetching and links unchanged; typecheck passes.
**Risk:** low

### Task 005 — Translate Settings page

**Goal:** Translate all section titles, descriptions, option labels, and buttons on the settings page.
**Scope:** Static UI text in `app/settings/page.tsx`; do not change setting keys, form field `name`s, or values sent to the API.
**Suggested files:** `app/settings/page.tsx`
**Acceptance criteria:** All settings UI text in Russian; saved settings payload/keys unchanged; typecheck passes.
**Risk:** medium

### Task 006 — Translate Reading List page

**Goal:** Translate the reading-list title, filter buttons, and empty-state messages to Russian.
**Scope:** Static UI text in `app/reading-list/page.tsx`; do not change filter values used in state/queries.
**Suggested files:** `app/reading-list/page.tsx`
**Acceptance criteria:** All reading-list UI text in Russian; filtering logic and toast triggers unchanged; typecheck passes.
**Risk:** low

### Task 007 — Translate Collections page

**Goal:** Translate all UI labels, buttons, confirm-modal messages, and toast strings on the collections page.
**Scope:** Static UI text and the title/message strings passed into `ConfirmModal`/`Toast` from `app/collections/page.tsx`.
**Suggested files:** `app/collections/page.tsx`
**Acceptance criteria:** No English UI text remains; confirm/toast messages in Russian; CRUD logic and API calls unchanged; typecheck passes.
**Risk:** low

### Task 008 — Translate Feedback page

**Goal:** Translate the feedback page labels, KPI captions, and filter buttons to Russian.
**Scope:** Static UI text in `app/feedback/page.tsx`, including the labels passed to `KpiCard`.
**Suggested files:** `app/feedback/page.tsx`
**Acceptance criteria:** All feedback UI text in Russian; metrics/data and filter values unchanged; typecheck passes.
**Risk:** low

### Task 009 — Translate SummaryCards component

**Goal:** Translate the hardcoded card labels ("Collected", "Selected", "Potentially Relevant", "Trends") to Russian.
**Scope:** Static label strings in `components/SummaryCards.tsx`.
**Suggested files:** `components/SummaryCards.tsx`
**Acceptance criteria:** All four+ card labels render in Russian; numeric/data props unchanged; typecheck passes.
**Risk:** low

### Task 010 — Translate StrategicSignals component

**Goal:** Translate the strategic-signal group names ("Product Launches", "Partnerships", etc.) and any section headers to Russian.
**Scope:** Static display labels in `components/StrategicSignals.tsx`. If group names are also used as data/lookup keys, translate only the displayed label, not the key.
**Suggested files:** `components/StrategicSignals.tsx`
**Acceptance criteria:** Group display names render in Russian; any key-based grouping logic preserved; typecheck passes.
**Risk:** medium

### Task 011 — Translate ExecutiveSummary and report section headers

**Goal:** Translate the "Executive Summary" heading and any other static section labels in the executive summary view.
**Scope:** Static text in `components/ExecutiveSummary.tsx`.
**Suggested files:** `components/ExecutiveSummary.tsx`
**Acceptance criteria:** Section headers in Russian; content props unchanged; typecheck passes.
**Risk:** low

### Task 012 — Translate StatsPanel remaining English

**Goal:** Translate the still-English section titles in StatsPanel (labels are already Russian) to Russian.
**Scope:** Static section-title strings in `components/StatsPanel.tsx`.
**Suggested files:** `components/StatsPanel.tsx`
**Acceptance criteria:** All StatsPanel section titles in Russian; metric values unchanged; typecheck passes.
**Risk:** low

### Task 013 — Translate progress views ("Analyzing" headers)

**Goal:** Translate the remaining English headers in the progress components (steps are already Russian, "Analyzing" header is English).
**Scope:** Static header/status text in `components/ProgressTimeline.tsx` and `components/ProgressView.tsx`.
**Suggested files:** `components/ProgressTimeline.tsx`, `components/ProgressView.tsx`
**Acceptance criteria:** All progress UI text in Russian; step/state logic unchanged; typecheck passes.
**Risk:** low

### Task 014 — Translate NewsCard remaining English

**Goal:** Translate the "AI summary" label and any mixed-language action button labels in NewsCard.
**Scope:** Static label/button text in `components/NewsCard.tsx`; dynamic headline/content untouched.
**Suggested files:** `components/NewsCard.tsx`
**Acceptance criteria:** All NewsCard static labels/buttons in Russian; action handlers and props unchanged; typecheck passes.
**Risk:** low

### Task 015 — Finish home page (page.tsx) remaining English

**Goal:** Translate the remaining English intro/hero/inline text on the home page (form is mostly Russian already).
**Scope:** Remaining English static text in `app/page.tsx` not covered by component-level tasks.
**Suggested files:** `app/page.tsx`
**Acceptance criteria:** No English UI text remains on the home page; mode/source logic and API params unchanged; typecheck passes. Best done after Tasks 003/009 to avoid overlap.
**Risk:** low

### Task 016 — Finish Sources page remaining English labels

**Goal:** Translate the leftover English form labels ("Time window", "Category", "Tags", "Active") on the already-mostly-Russian sources page.
**Scope:** Remaining English static labels in `app/sources/page.tsx`; do not change field names or values.
**Suggested files:** `app/sources/page.tsx`
**Acceptance criteria:** No English UI text remains; form submission payload unchanged; typecheck passes.
**Risk:** low

### Task 017 — Finish Profiles page remaining English labels

**Goal:** Translate the leftover English keyword-editor labels ("Include keywords", "Exclude keywords") on the profiles page.
**Scope:** Remaining English static labels in `app/profiles/page.tsx`; keep keyword data/keys intact.
**Suggested files:** `app/profiles/page.tsx`
**Acceptance criteria:** No English UI text remains; profile save logic unchanged; typecheck passes.
**Risk:** low

### Task 018 — Finish Login page ("Sign In" button)

**Goal:** Translate the remaining English "Sign In" submit button (form labels already Russian).
**Scope:** Button/static text in `app/login/page.tsx`.
**Suggested files:** `app/login/page.tsx`
**Acceptance criteria:** Submit button and any remaining text in Russian; auth flow unchanged; typecheck passes.
**Risk:** low

### Task 019 — Finish Benchmark page remaining English

**Goal:** Translate remaining mixed-language text on the benchmark page, including English table headers in BenchmarkTable.
**Scope:** Remaining English static text in `app/benchmark/page.tsx` and column headers/labels in `components/BenchmarkTable.tsx`.
**Suggested files:** `app/benchmark/page.tsx`, `components/BenchmarkTable.tsx`
**Acceptance criteria:** No English UI text remains on benchmark view; metric data and sort keys unchanged; typecheck passes.
**Risk:** low

### Task 020 — Translate SourcePicker and PreviewPanel remaining English

**Goal:** Translate "Upload TXT file" / "RSS Collection" in SourcePicker and the "AI summaries" button in PreviewPanel.
**Scope:** Static label/button text in `components/SourcePicker.tsx` and `components/PreviewPanel.tsx`.
**Suggested files:** `components/SourcePicker.tsx`, `components/PreviewPanel.tsx`
**Acceptance criteria:** All static labels/buttons in Russian; selection/preview logic unchanged; typecheck passes.
**Risk:** low

### Task 021 — Sweep for residual English UI strings

**Goal:** Final pass to catch any remaining hardcoded English UI strings missed by earlier tasks (e.g. ErrorState, ModeSelector, dynamic toast/error messages, ExportButtons descriptive text).
**Scope:** Grep across `app/**` and `components/**` for residual English visible strings; translate any found. Do not touch logs, identifiers, or non-UI strings.
**Suggested files:** `components/ErrorState.tsx`, `components/ModeSelector.tsx`, and any others surfaced by the sweep.
**Acceptance criteria:** A documented grep sweep shows no remaining visible English UI text; typecheck passes. Run last, after Tasks 001–020.
**Risk:** medium

---

**Sequencing notes:** Tasks 001–003 (shared, globally visible) first for immediate impact. Tasks 004–008 are fully-English standalone pages — fully parallelizable. Tasks 009–014 are shared report/display components. Tasks 015–020 finish partially-translated files (do after their related component tasks to avoid edit overlap). Task 021 is the closing sweep and should run last.
