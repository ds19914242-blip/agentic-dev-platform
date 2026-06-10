### Task 017 — Translate residual components (StatsPanel, TrendsPanel, StrategicSignals, ExecutiveSummary, ProgressView, PreviewPanel, ProfileSelector)

**Goal:** Sweep remaining shared report/analysis components for any English visible text.
**Scope:** Audit and translate any leftover English strings, labels, headings, and empty states in these components. Each is small; group as one PR. (PreviewPanel and ProfileSelector are partially Russian — finish them.)
**Suggested files:** `components/StatsPanel.tsx`, `components/TrendsPanel.tsx`, `components/StrategicSignals.tsx`, `components/ExecutiveSummary.tsx`, `components/ProgressView.tsx`, `components/PreviewPanel.tsx`, `components/ProfileSelector.tsx`
**Acceptance criteria:** None of these components render English visible text; data/props unchanged; typecheck passes.
**Risk:** medium
