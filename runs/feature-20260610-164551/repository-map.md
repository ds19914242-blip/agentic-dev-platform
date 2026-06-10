# Repository Map

## api_routes

- app/api/analyze/route.ts
- app/api/auth/login/route.ts
- app/api/auth/logout/route.ts
- app/api/benchmark/route.ts
- app/api/favorites/[id]/route.ts
- app/api/favorites/route.ts
- app/api/feedback/route.ts
- app/api/health/db/route.ts
- app/api/health/route.ts
- app/api/jobs/[jobId]/route.ts
- app/api/overview/route.ts
- app/api/profiles/[id]/route.ts
- app/api/profiles/route.ts
- app/api/report/[id]/docx/route.ts
- app/api/report/[id]/json/route.ts
- app/api/report/[id]/markdown/route.ts
- app/api/report/[id]/pdf/route.ts
- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/summarize/route.ts
- app/api/rss/test/route.ts
- app/api/runs/[id]/route.ts
- app/api/runs/route.ts
- app/api/settings/route.ts
- app/api/upload/route.ts

## pages

- app/benchmark/page.tsx
- app/collections/page.tsx
- app/dashboard/page.tsx
- app/feedback/page.tsx
- app/history/page.tsx
- app/login/page.tsx
- app/page.tsx
- app/profiles/page.tsx
- app/reading-list/page.tsx
- app/reports/page.tsx
- app/rss/collections/page.tsx
- app/rss/page.tsx
- app/run/[id]/page.tsx
- app/settings/page.tsx
- app/sources/page.tsx
- app/templates/page.tsx
- app/workspace/page.tsx

## components

- components/BenchmarkTable.tsx
- components/ConfirmModal.tsx
- components/Dashboard.tsx
- components/ErrorState.tsx
- components/ExecutiveSummary.tsx
- components/ExportButtons.tsx
- components/Footer.tsx
- components/Hero.tsx
- components/KpiCard.tsx
- components/ModeSelector.tsx
- components/NavBar.tsx
- components/NewsCard.tsx
- components/PreviewPanel.tsx
- components/ProfileSelector.tsx
- components/ProgressTimeline.tsx
- components/ProgressView.tsx
- components/SourcePicker.tsx
- components/StatsPanel.tsx
- components/StrategicSignals.tsx
- components/SummaryCards.tsx
- components/Toast.tsx
- components/TopicSelector.tsx
- components/TrendsPanel.tsx
- components/UploadDropzone.tsx
- components/charts/CategoryChart.tsx
- components/charts/ExclusionChart.tsx
- components/charts/MatchedExcludedChart.tsx
- components/charts/SourceChart.tsx
- components/charts/theme.ts

## llm

- src/llm/client.ts

## agents

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts

## storage

- lib/storage/index.ts
- lib/storage/local.ts
- lib/storage/postgres.ts
- lib/storage/rss.ts
- lib/storage/types.ts

## rss

- lib/recordFeedback.ts
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/analysis/feedbackRanking.ts
- src/collector/fetchFeeds.ts
- src/config/feeds.ts
- src/importers/parseRssTextFile.ts

## config

- src/config.ts
- tsconfig.json

## tests

_None detected_

## other

- README.md
- app/globals.css
- app/layout.tsx
- lib/analysisCache.ts
- lib/dashboard.ts
- lib/db.ts
- lib/export/docx.ts
- lib/export/pdf.ts
- lib/jobStore.ts
- lib/saveFavorite.ts
- lib/session.ts
- lib/telegram/fetchTelegramChannel.ts
- lib/uploadPreview.ts
- lib/version.ts
- package.json
- src/analysis/criteria.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/debugParser.ts
- src/importers/loadArticlesJson.ts
- src/index.ts
- src/metrics/runMetrics.ts
- src/prefilter/prefilterArticles.ts
- src/processing/cleanHtml.ts
- src/processing/deduplicate.ts
- src/report.ts
- src/reportJson.ts
- src/reporting/renderCustomerReport.ts
- src/reporting/transparency.ts
- src/storage/store.ts
- src/types/article.ts
- src/types/report.ts
- src/util/progress.ts
- src/workflows/customerTopNewsWorkflow.ts
