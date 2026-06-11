# Import Map

## app/api/analyze/route.ts

- next/server
- ../../../lib/jobStore.js
- ../../../src/analysis/criteria.js

## app/api/auth/login/route.ts

- node:crypto
- next/server

## app/api/auth/logout/route.ts

- next/server
- ../../../../lib/session.js

## app/api/benchmark/route.ts

- next/server
- ../../../src/analysis/criteria.js
- ../../../src/analysis/performance.js

## app/api/favorites/[id]/route.ts

- next/server
- ../../../../lib/storage/index.js

## app/api/favorites/route.ts

- next/server
- ../../../lib/storage/index.js

## app/api/feedback/route.ts

- next/server
- ../../../lib/storage/index.js
- ../../../lib/storage/types.js

## app/api/health/db/route.ts

- next/server
- ../../../../lib/db.js

## app/api/health/route.ts

- next/server
- ../../../lib/db.js

## app/api/jobs/[jobId]/route.ts

- next/server
- ../../../../lib/jobStore.js

## app/api/overview/route.ts

- next/server

## app/api/profiles/[id]/route.ts

- next/server
- ../../../../lib/storage/index.js
- ../../../../lib/storage/types.js
- ../../../../src/analysis/performance.js

## app/api/profiles/route.ts

- node:crypto
- next/server
- ../../../lib/storage/index.js
- ../../../lib/storage/types.js
- ../../../src/analysis/performance.js

## app/api/report/[id]/docx/route.ts

- node:path
- next/server
- ../../../../../lib/storage/index.js
- ../../../../../lib/export/docx.js

## app/api/report/[id]/json/route.ts

- node:fs/promises
- node:path
- next/server

## app/api/report/[id]/markdown/route.ts

- node:fs/promises
- node:path
- next/server

## app/api/report/[id]/pdf/route.ts

- node:path
- next/server
- ../../../../../lib/storage/index.js
- ../../../../../lib/export/pdf.js

## app/api/rss/collect/route.ts

- next/server
- ../../../../lib/rss/collect.js
- ../../../../lib/jobStore.js

## app/api/rss/collections/[id]/route.ts

- next/server
- ../../../../../lib/storage/index.js

## app/api/rss/collections/route.ts

- next/server
- ../../../../lib/storage/index.js

## app/api/rss/sources/[id]/route.ts

- next/server
- ../../../../../lib/storage/index.js
- ../../../../../lib/storage/types.js

## app/api/rss/sources/route.ts

- next/server
- ../../../../lib/storage/index.js

## app/api/rss/summarize/route.ts

- next/server
- ../../../../lib/jobStore.js
- ../../../../src/agents/summaryBatchAgent.js

## app/api/rss/test/route.ts

- next/server
- ../../../../lib/rss/fetchFeed.js

## app/api/runs/[id]/route.ts

- next/server

## app/api/runs/route.ts

- next/server
- ../../../lib/storage/index.js

## app/api/settings/route.ts

- next/server
- ../../../lib/storage/index.js
- ../../../lib/storage/types.js

## app/api/upload/route.ts

- next/server
- ../../../lib/jobStore.js

## app/benchmark/page.tsx

- react
- ../../lib/dashboard.js
- ../../components/UploadDropzone.js
- ../../components/TopicSelector.js
- ../../components/BenchmarkTable.js

## app/collections/page.tsx

- react
- next/navigation
- ../../lib/storage/types.js
- ../../components/Toast.js
- ../../components/ConfirmModal.js

## app/dashboard/page.tsx

- react
- next/link
- ../../lib/storage/types.js

## app/feedback/page.tsx

- react
- ../../lib/storage/types.js
- ../../components/KpiCard.js

## app/history/page.tsx

- next/navigation

## app/layout.tsx

- next
- next/font/google
- ../components/NavBar.js
- ../components/Footer.js
- ../components/Toast.js

## app/login/page.tsx

- react
- next/navigation

## app/page.tsx

- react
- ../lib/dashboard.js
- ../src/analysis/performance.js
- ../lib/storage/types.js
- ../components/Hero.js
- ../components/SourcePicker.js
- ../components/UploadDropzone.js
- ../components/PreviewPanel.js
- ../components/ProfileSelector.js
- ../components/TopicSelector.js
- ../components/ModeSelector.js
- ../components/ProgressTimeline.js
- ../components/ErrorState.js
- ../components/Dashboard.js

## app/profiles/page.tsx

- react
- ../../lib/storage/types.js
- ../../src/analysis/criteria.js
- ../../src/analysis/performance.js
- ../../components/Toast.js
- ../../components/ConfirmModal.js

## app/reading-list/page.tsx

- react
- ../../lib/storage/types.js
- ../../components/Toast.js

## app/reports/page.tsx

- react
- next/link
- ../../lib/storage/types.js
- ../../src/analysis/performance.js
- ../../components/Toast.js
- ../../components/ConfirmModal.js

## app/rss/collections/page.tsx

- next/navigation

## app/rss/page.tsx

- next/navigation

## app/run/[id]/page.tsx

- react
- next/navigation
- next/link
- ../../../lib/dashboard.js
- ../../../lib/storage/types.js
- ../../../components/Dashboard.js

## app/settings/page.tsx

- react
- ../../lib/storage/types.js
- ../../components/Toast.js

## app/sources/page.tsx

- react
- ../../lib/storage/types.js
- ../../components/Toast.js
- ../../components/ConfirmModal.js

## app/templates/page.tsx

- next/navigation

## app/workspace/page.tsx

- next/navigation

## components/BenchmarkTable.tsx

- ../lib/dashboard.js
- ../src/analysis/performance.js

## components/Dashboard.tsx

- ../lib/dashboard.js
- ./ExportButtons.js
- ./SummaryCards.js
- ./ExecutiveSummary.js
- ./TrendsPanel.js
- ./StrategicSignals.js
- ./NewsCard.js
- ./StatsPanel.js
- ./charts/CategoryChart.js
- ./charts/ExclusionChart.js
- ./charts/MatchedExcludedChart.js
- ./charts/SourceChart.js

## components/ExecutiveSummary.tsx

- ../src/types/report.js

## components/Footer.tsx

- ../lib/version.js

## components/ModeSelector.tsx

- ../src/analysis/performance.js

## components/NavBar.tsx

- next/link
- next/navigation

## components/NewsCard.tsx

- react
- ../src/types/report.js
- ../lib/storage/types.js
- ../lib/recordFeedback.js
- ../lib/saveFavorite.js

## components/PreviewPanel.tsx

- react
- ../lib/dashboard.js
- ./KpiCard.js

## components/ProfileSelector.tsx

- react
- ../lib/storage/types.js

## components/ProgressTimeline.tsx

- ../lib/dashboard.js

## components/ProgressView.tsx

- ../lib/dashboard.js

## components/StatsPanel.tsx

- ../src/types/report.js

## components/StrategicSignals.tsx

- ../src/types/report.js

## components/SummaryCards.tsx

- ../lib/dashboard.js
- ./KpiCard.js

## components/Toast.tsx

- react

## components/TopicSelector.tsx

- react

## components/TrendsPanel.tsx

- ../src/types/report.js

## components/UploadDropzone.tsx

- react

## components/charts/CategoryChart.tsx

- ../../src/types/report.js
- ./theme.js

## components/charts/ExclusionChart.tsx

- ../../src/types/report.js
- ./theme.js

## components/charts/MatchedExcludedChart.tsx

- ../../src/types/report.js
- ./theme.js

## components/charts/SourceChart.tsx

- ../../src/types/report.js
- ./theme.js

## lib/analysisCache.ts

- node:crypto
- ../src/analysis/criteria.js
- ../src/types/report.js
- ./storage/index.js
- ./storage/types.js

## lib/dashboard.ts

- ../src/types/report.js
- ./uploadPreview.js

## lib/db.ts

- pg

## lib/export/docx.ts

- ../../src/types/report.js

## lib/export/pdf.ts

- node:path
- pdfkit
- ../../src/types/report.js

## lib/jobStore.ts

- node:fs/promises
- node:path
- node:crypto
- ../src/importers/parseRssTextFile.js
- ../src/workflows/customerTopNewsWorkflow.js
- ../src/reporting/renderCustomerReport.js
- ../src/analysis/feedbackRanking.js
- ../src/types/report.js
- ../src/analysis/criteria.js
- ./uploadPreview.js
- ./storage/types.js

## lib/recordFeedback.ts

- ./storage/types.js

## lib/rss/collect.ts

- ../storage/index.js
- ./fetchFeed.js

## lib/rss/fetchFeed.ts

- rss-parser

## lib/storage/index.ts

- ../db.js

## lib/storage/local.ts

- node:fs/promises
- node:path
- node:crypto
- ../../src/types/report.js
- ../../src/analysis/profiles.js
- ./types.js

## lib/storage/postgres.ts

- ../../src/types/report.js
- ../db.js
- ../../src/analysis/profiles.js
- ./types.js
- ../../src/analysis/performance.js
- node:crypto

## lib/storage/rss.ts

- node:fs/promises
- node:path
- node:crypto

## lib/storage/types.ts

- ../../src/types/report.js
- ../../src/types/report.js
- ../../src/analysis/performance.js

## lib/telegram/fetchTelegramChannel.ts

- sanitize-html

## lib/uploadPreview.ts

- ../src/types/report.js
- ../src/types/report.js

## lib/version.ts

- ../package.json

## src/agents/criteriaBatchAgent.ts

- zod
- @anthropic-ai/sdk/helpers/zod
- ../llm/client.js
- ../metrics/runMetrics.js
- ../types/report.js

## src/agents/summaryBatchAgent.ts

- zod
- @anthropic-ai/sdk/helpers/zod
- ../llm/client.js
- ../metrics/runMetrics.js
- ../types/report.js

## src/agents/trendAnalysisAgent.ts

- zod
- @anthropic-ai/sdk/helpers/zod
- ../llm/client.js
- ../metrics/runMetrics.js
- ../analysis/criteria.js
- ../types/report.js

## src/analysis/criteria.ts

- ./performance.js

## src/analysis/feedbackRanking.ts

- ../../lib/storage/types.js
- ../../lib/storage/types.js
- ../types/report.js

## src/analysis/profiles.ts

- ../../lib/storage/types.js

## src/collector/fetchFeeds.ts

- rss-parser
- ../config/feeds.js
- ../types/article.js

## src/debugParser.ts

- node:fs
- node:path
- ./importers/parseRssTextFile.js

## src/importers/loadArticlesJson.ts

- node:fs
- ../types/article.js
- ../types/report.js

## src/importers/parseRssTextFile.ts

- node:fs
- ../processing/cleanHtml.js
- ../types/report.js

## src/index.ts

- ./collector/fetchFeeds.js
- ./processing/deduplicate.js
- ./storage/store.js

## src/llm/client.ts

- @anthropic-ai/sdk

## src/prefilter/prefilterArticles.ts

- ../types/report.js

## src/processing/cleanHtml.ts

- sanitize-html

## src/processing/deduplicate.ts

- node:crypto
- ../types/article.js
- ./cleanHtml.js

## src/report.ts

- node:fs
- node:path
- ./workflows/customerTopNewsWorkflow.js
- ./reporting/renderCustomerReport.js

## src/reportJson.ts

- node:fs
- node:path
- ./importers/loadArticlesJson.js
- ./workflows/customerTopNewsWorkflow.js
- ./reporting/renderCustomerReport.js
- ./config.js

## src/storage/store.ts

- node:fs/promises
- node:path
- ../types/article.js

## src/workflows/customerTopNewsWorkflow.ts

- node:path
- ../importers/parseRssTextFile.js
- ../agents/criteriaBatchAgent.js
- ../agents/trendAnalysisAgent.js
- ../prefilter/prefilterArticles.js
- ../config.js
- ../metrics/runMetrics.js
- ../util/progress.js
- ../llm/client.js
- ../analysis/performance.js
- ../../lib/analysisCache.js
