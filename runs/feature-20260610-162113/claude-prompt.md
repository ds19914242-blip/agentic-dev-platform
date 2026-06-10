# Feature Request

Add a small Russian helper text under the reports page title explaining that generated reports can be reviewed and exported here

# Repository

/Users/danilsmetanev/Projects/rss-agent-lab_2

# Execution Mode

plan_only

# Affected Files

- app/api/report/[id]/docx/route.ts
- app/api/report/[id]/json/route.ts
- app/api/report/[id]/markdown/route.ts
- app/api/report/[id]/pdf/route.ts
- src/reportJson.ts
- app/reports/page.tsx
- lib/export/docx.ts
- lib/export/pdf.ts
- src/importers/loadArticlesJson.ts
- src/report.ts
- src/reporting/renderCustomerReport.ts
- src/reporting/transparency.ts

# Task

Create a detailed implementation plan.

Do not modify files.
Stop after the plan.

# Rules

- Start by inspecting the affected files directly from the repository.
- Prefer the smallest safe implementation.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- If uncertain, stop and explain the uncertainty.
