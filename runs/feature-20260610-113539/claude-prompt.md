# Feature Request

Show AI summaries in RSS preview before analysis

# Repository

/Users/danilsmetanev/Projects/rss-agent-lab_2

# Affected Files

- app/api/rss/collect/route.ts
- app/api/rss/collections/[id]/route.ts
- app/api/rss/collections/route.ts
- app/api/rss/sources/[id]/route.ts
- app/api/rss/sources/route.ts
- app/api/rss/summarize/route.ts
- app/api/rss/test/route.ts
- app/rss/collections/page.tsx
- app/rss/page.tsx
- components/BenchmarkTable.tsx
- components/ConfirmModal.tsx
- components/Dashboard.tsx
- components/ErrorState.tsx
- components/ExecutiveSummary.tsx
- components/ExportButtons.tsx

# Task

You are a senior autonomous coding agent.

Analyze the affected files and implement the smallest safe solution.

Rules:
- First explain what already exists.
- Then create an implementation plan.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- After implementation, run typecheck/tests if available.
- Summarize changed files and risks.

# Context



# FILE: app/api/rss/collect/route.ts

import { NextResponse } from "next/server";
import { collectCollection } from "../../../../lib/rss/collect.js";
import { saveUpload } from "../../../../lib/jobStore.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/rss/collect — collect articles for a collection, serialize them
 * into the parser's text format, and save them as a normal upload. Returns the
 * same upload preview as /api/upload PLUS collection stats — so the caller can
 * continue through the EXISTING analyze flow (profile → topics → mode → run).
 */
export async function POST(request: Request) {
  let body: { collectionId?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }
  if (!body.collectionId) {
    return NextResponse.json({ error: "collectionId is required." }, { status: 400 });
  }

  const result = await collectCollection(body.collectionId);
  if (!result.ok || !result.stats) {
    return NextResponse.json(
      { error: result.error ?? "Collection failed." },
      { status: 400 },
    );
  }
  if (result.stats.totalArticles === 0) {
    return NextResponse.json(
      { error: "No articles collected (check that sources are active and reachable).", stats: result.stats },
      { status: 422 },
    );
  }

  const preview = await saveUpload(result.fileName ?? "collection.rss", result.text ?? "");
  return NextResponse.json({ ...preview, stats: result.stats });
}


# FILE: app/api/rss/collections/[id]/route.ts

import { NextResponse } from "next/server";
import { rssCollectionStorage } from "../../../../../lib/storage/index.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** PATCH /api/rss/collections/:id — update name/description/sourceIds. */
export async function PATCH(
  request: Request,
  { params }: { params: { id: string } },
) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }

  const patch: Record<string, unknown> = {};
  if (typeof body.name === "string") {
    if (!body.name.trim()) return NextResponse.json({ error: "Name is required." }, { status: 400 });
    patch.name = body.name;
  }
  if (typeof body.description === "string") patch.description = body.description;
  if (Array.isArray(body.sourceIds)) patch.sourceIds = body.sourceIds;

  const updated = await rssCollectionStorage.update(params.id, patch);
  if (!updated) return NextResponse.json({ error: "Collection not found." }, { status: 404 });
  return NextResponse.json({ collection: updated });
}

/** DELETE /api/rss/collections/:id */
export async function DELETE(
  _request: Request,
  { params }: { params: { id: string } },
) {
  await rssCollectionStorage.delete(params.id);
  return NextResponse.json({ ok: true });
}


# FILE: app/api/rss/collections/route.ts

import { NextResponse } from "next/server";
import { rssCollectionStorage } from "../../../../lib/storage/index.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** GET /api/rss/collections — list all collections. */
export async function GET() {
  const collections = await rssCollectionStorage.list();
  return NextResponse.json({ collections });
}

/** POST /api/rss/collections — create a collection. */
export async function POST(request: Request) {
  let body: {
    name?: string;
    description?: string;
    sourceIds?: string[];
  };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }
  if (!body.name?.trim()) {
    return NextResponse.json({ error: "Name is required." }, { status: 400 });
  }
  const collection = await rssCollectionStorage.create({
    name: body.name,
    description: body.description ?? "",
    sourceIds: Array.isArray(body.sourceIds) ? body.sourceIds : [],
  });
  return NextResponse.json({ collection });
}


# FILE: app/api/rss/sources/[id]/route.ts

import { NextResponse } from "next/server";
import { rssSourceStorage } from "../../../../../lib/storage/index.js";
import { RSS_CATEGORIES, type RssCategory } from "../../../../../lib/storage/types.js";
import {
  TELEGRAM_DEFAULT_MAX_POSTS,
  TELEGRAM_DEFAULT_WINDOW_DAYS,
  TELEGRAM_MAX_POSTS_CAP,
  normalizeTelegram,
} from "../../../../../lib/telegram/fetchTelegramChannel.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** PATCH /api/rss/sources/:id — update an RSS or Telegram source (partial). */
export async function PATCH(
  request: Request,
  { params }: { params: { id: string } },
) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }

  const existing = await rssSourceStorage.get(params.id);
  if (!existing) return NextResponse.json({ error: "Source not found." }, { status: 404 });

  const patch: Record<string, unknown> = {};
  if (typeof body.name === "string") {
    if (!body.name.trim()) return NextResponse.json({ error: "Name is required." }, { status: 400 });
    patch.name = body.name;
  }
  if (typeof body.category === "string" && RSS_CATEGORIES.includes(body.category as RssCategory)) {
    patch.category = body.category;
  }
  if (Array.isArray(body.tags)) patch.tags = body.tags;
  if (typeof body.isActive === "boolean") patch.isActive = body.isActive;

  const targetType =
    (body.sourceType as string) ?? existing.sourceType ?? "rss";

  if (targetType === "telegram") {
    if (typeof body.url === "string" && body.url.trim()) {
      const norm = normalizeTelegram(body.url);
      if (!norm) {
        return NextResponse.json(
          { error: "A valid Telegram channel URL or @username is required." },
          { status: 400 },
        );
      }
      patch.url = norm.webUrl;
      patch.sourceType = "telegram";
      patch.telegram = {
        channelUsername: norm.channelUsername,
        webUrl: norm.webUrl,
        maxPosts: clampPosts(body.maxPosts ?? existing.telegram?.maxPosts),
        timeWindowDays: clampWindow(body.timeWindowDays ?? existing.telegram?.timeWindowDays),
      };
    } else if (existing.telegram) {
      // Update only the telegram limits.
      patch.telegram = {
        ...existing.telegram,
        maxPosts: clampPosts(body.maxPosts ?? existing.telegram.maxPosts),
        timeWindowDays: clampWindow(body.timeWindowDays ?? existing.telegram.timeWindowDays),
      };
    }
  } else if (typeof body.url === "string") {
    if (!/^https?:\/\//i.test(body.url.trim())) {
      return NextResponse.json(
        { error: "URL must start with http:// or https://" },
        { status: 400 },
      );
    }
    patch.url = body.url;
    patch.sourceType = "rss";
  }

  const updated = await rssSourceStorage.update(params.id, patch);
  return NextResponse.json({ source: updated });
}

/** DELETE /api/rss/sources/:id */
export async function DELETE(
  _request: Request,
  { params }: { params: { id: string } },
) {
  await rssSourceStorage.delete(params.id);
  return NextResponse.json({ ok: true });
}

function clampPosts(v: unknown): number {
  const n = Number(v);
  if (!Number.isFinite(n)) return TELEGRAM_DEFAULT_MAX_POSTS;
  return Math.min(TELEGRAM_MAX_POSTS_CAP, Math.max(1, Math.floor(n)));
}
function clampWindow(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : TELEGRAM_DEFAULT_WINDOW_DAYS;
}


# FILE: app/api/rss/sources/route.ts

import { NextResponse } from "next/server";
import { rssSourceStorage } from "../../../../lib/storage/index.js";
import {
  RSS_CATEGORIES,
  type RssCategory,
  type SourceType,
} from "../../../../lib/storage/types.js";
import {
  TELEGRAM_DEFAULT_MAX_POSTS,
  TELEGRAM_DEFAULT_WINDOW_DAYS,
  TELEGRAM_MAX_POSTS_CAP,
  normalizeTelegram,
} from "../../../../lib/telegram/fetchTelegramChannel.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

interface SourceBody {
  name?: string;
  url?: string;
  category?: string;
  tags?: string[];
  isActive?: boolean;
  sourceType?: SourceType;
  maxPosts?: number;
  timeWindowDays?: number;
}

function clampPosts(v: unknown): number {
  const n = Number(v);
  if (!Number.isFinite(n)) return TELEGRAM_DEFAULT_MAX_POSTS;
  return Math.min(TELEGRAM_MAX_POSTS_CAP, Math.max(1, Math.floor(n)));
}
function clampWindow(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : TELEGRAM_DEFAULT_WINDOW_DAYS;
}

/** GET /api/rss/sources — list all sources. */
export async function GET() {
  const sources = await rssSourceStorage.list();
  return NextResponse.json({ sources });
}

/** POST /api/rss/sources — create an RSS or Telegram source. */
export async function POST(request: Request) {
  let body: SourceBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }
  if (!body.name?.trim()) {
    return NextResponse.json({ error: "Name is required." }, { status: 400 });
  }
  const category = RSS_CATEGORIES.includes(body.category as RssCategory)
    ? (body.category as RssCategory)
    : "Other";
  const tags = Array.isArray(body.tags) ? body.tags : [];

  if (body.sourceType === "telegram") {
    const norm = normalizeTelegram(body.url ?? "");
    if (!norm) {
      return NextResponse.json(
        { error: "A valid Telegram channel URL or @username is required." },
        { status: 400 },
      );
    }
    const source = await rssSourceStorage.create({
      name: body.name,
      url: norm.webUrl,
      category,
      tags,
      isActive: body.isActive ?? true,
      sourceType: "telegram",
      telegram: {
        channelUsername: norm.channelUsername,
        webUrl: norm.webUrl,
        maxPosts: clampPosts(body.maxPosts),
        timeWindowDays: clampWindow(body.timeWindowDays),
      },
    });
    return NextResponse.json({ source });
  }

  // RSS (default)
  const url = body.url?.trim();
  if (!url) return NextResponse.json({ error: "RSS URL is required." }, { status: 400 });
  if (!/^https?:\/\//i.test(url)) {
    return NextResponse.json(
      { error: "URL must start with http:// or https://" },
      { status: 400 },
    );
  }
  const source = await rssSourceStorage.create({
    name: body.name,
    url,
    category,
    tags,
    isActive: body.isActive ?? true,
    sourceType: "rss",
  });
  return NextResponse.json({ source });
}


# FILE: app/api/rss/summarize/route.ts

import { NextResponse } from "next/server";
import { parseUpload, uploadExists } from "../../../../lib/jobStore.js";
import { summaryBatchAgent } from "../../../../src/agents/summaryBatchAgent.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** How many of the previewed articles get an AI summary (matches the preview sample). */
const PREVIEW_SAMPLE = 10;

/**
 * POST /api/rss/summarize — on-demand AI summaries for the preview sample of a
 * previously-uploaded/collected file. Body: { uploadId }. Returns
 * { summaries: { number, summaryRu }[] }. Opt-in: Claude is only called here
 * when the user clicks "Generate AI summaries" in the preview.
 */
export async function POST(request: Request) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json(
      { error: "ANTHROPIC_API_KEY is not set on the server." },
      { status: 500 },
    );
  }

  let body: { uploadId?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Expected JSON body." }, { status: 400 });
  }

  if (!body.uploadId) {
    return NextResponse.json({ error: "Missing uploadId." }, { status: 400 });
  }
  if (!(await uploadExists(body.uploadId))) {
    return NextResponse.json(
      { error: "Upload not found. Please upload the file again." },
      { status: 404 },
    );
  }

  try {
    const { articles } = parseUpload(body.uploadId);
    const sample = articles.slice(0, PREVIEW_SAMPLE);
    if (sample.length === 0) {
      return NextResponse.json({ summaries: [] });
    }
    const summaries = await summaryBatchAgent(sample);
    return NextResponse.json({ summaries });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Summary generation failed." },
      { status: 502 },
    );
  }
}


# FILE: app/api/rss/test/route.ts

import { NextResponse } from "next/server";
import { fetchFeed } from "../../../../lib/rss/fetchFeed.js";
import {
  fetchTelegramChannel,
  normalizeTelegram,
} from "../../../../lib/telegram/fetchTelegramChannel.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/rss/test — fetch a source and report status + sample items.
 * Branches on sourceType: rss → RSS parser, telegram → public web reader.
 * Never throws.
 */
export async function POST(request: Request) {
  let body: {
    url?: string;
    sourceType?: string;
    maxPosts?: number;
    timeWindowDays?: number;
  };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON." }, { status: 400 });
  }

  if (body.sourceType === "telegram") {
    const norm = normalizeTelegram(body.url ?? "");
    if (!norm) {
      return NextResponse.json(
        { error: "A valid Telegram channel URL or @username is required." },
        { status: 400 },
      );
    }
    const res = await fetchTelegramChannel({
      channelUsername: norm.channelUsername,
      maxPosts: body.maxPosts,
      timeWindowDays: body.timeWindowDays,
    });
    return NextResponse.json({
      ok: res.ok,
      status: res.status,
      itemCount: res.itemCount,
      error: res.error,
      latestDate: res.latestDate,
      sample: res.articles.slice(0, 5).map((a) => a.title),
    });
  }

  // RSS (default)
  const url = body.url?.trim();
  if (!url || !/^https?:\/\//i.test(url)) {
    return NextResponse.json(
      { error: "A valid http(s) URL is required." },
      { status: 400 },
    );
  }
  const res = await fetchFeed(url);
  return NextResponse.json({
    ok: res.ok,
    status: res.status,
    itemCount: res.itemCount,
    error: res.error,
    sample: res.articles.slice(0, 5).map((a) => a.title),
  });
}


# FILE: app/rss/collections/page.tsx

import { redirect } from "next/navigation";
export default function RssCollectionsRedirect() {
  redirect("/collections");
}


# FILE: app/rss/page.tsx

import { redirect } from "next/navigation";
export default function RssRedirect() {
  redirect("/sources");
}


# FILE: components/BenchmarkTable.tsx

import type { ReportData } from "../lib/dashboard.js";
import type { PerformanceMode } from "../src/analysis/performance.js";

export interface BenchRow {
  mode: PerformanceMode;
  jobId: string;
  status: "pending" | "running" | "done" | "error";
  result?: ReportData;
}

function topCats(data?: ReportData): string {
  if (!data) return "—";
  return (
    data.categoryDistribution
      .filter((c) => c.count > 0)
      .slice(0, 3)
      .map((c) => c.label)
      .join(", ") || "—"
  );
}

export function BenchmarkTable({ rows }: { rows: BenchRow[] }) {
  const cell = "px-4 py-3 text-sm";
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[640px]">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-400">
            <th className={cell}>Метрика</th>
            {rows.map((r) => (
              <th key={r.mode} className={`${cell} font-semibold`}>
                {r.mode}{" "}
                {r.status !== "done" && (
                  <span className="text-[10px] font-normal text-slate-400">
                    ({r.status})
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {[
            ["Время", (d?: ReportData) => (d ? `${(d.technicalStats.executionMs / 1000).toFixed(1)}с` : "—")],
            ["Collected", (d?: ReportData) => (d ? String(d.totalFound) : "—")],
            ["Selected", (d?: ReportData) => (d ? String((d.topNews ?? d.items ?? []).length) : "—")],
            ["Из кэша", (d?: ReportData) => (d ? String(d.technicalStats.cachedItems ?? 0) : "—")],
            ["По критериям", (d?: ReportData) => (d ? String(d.matchedCount) : "—")],
            ["Трендов", (d?: ReportData) => (d ? String((d.trendAnalysis ?? d.trends).topTrends.length) : "—")],
            ["Топ-категории", (d?: ReportData) => topCats(d)],
          ].map(([label, fn]) => (
            <tr key={label as string}>
              <td className={`${cell} font-medium text-slate-600`}>{label as string}</td>
              {rows.map((r) => (
                <td key={r.mode} className={`${cell} tabular-nums text-slate-800`}>
                  {(fn as (d?: ReportData) => string)(r.result)}
                </td>
              ))}
            </tr>
          ))}
          <tr>
            <td className={`${cell} font-medium text-slate-600`}>Отчёт</td>
            {rows.map((r) => (
              <td key={r.mode} className={cell}>
                {r.status === "done" ? (
                  <a
                    href={`/run/${r.jobId}`}
                    className="text-xs font-semibold text-indigo-600 hover:underline"
                  >
                    Открыть
                  </a>
                ) : (
                  "—"
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}


# FILE: components/ConfirmModal.tsx

"use client";

export function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = "Удалить",
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30 p-4 backdrop-blur-sm"
      onClick={onCancel}
    >
      <div
        className="animate-rise w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold tracking-tight">{title}</h2>
        <p className="mt-2 text-sm text-slate-600">{message}</p>
        <div className="mt-6 flex justify-end gap-2">
          <button onClick={onCancel} className="btn-ghost">
            Отмена
          </button>
          <button
            onClick={onConfirm}
            className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-500"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}


# FILE: components/Dashboard.tsx

"use client";

import type { ReportData } from "../lib/dashboard.js";
import { ExportButtons } from "./ExportButtons.js";
import { SummaryCards } from "./SummaryCards.js";
import { ExecutiveSummary } from "./ExecutiveSummary.js";
import { TrendsPanel } from "./TrendsPanel.js";
import { StrategicSignals } from "./StrategicSignals.js";
import { NewsCard } from "./NewsCard.js";
import { StatsPanel } from "./StatsPanel.js";
import { CategoryChart } from "./charts/CategoryChart.js";
import { ExclusionChart } from "./charts/ExclusionChart.js";
import { MatchedExcludedChart } from "./charts/MatchedExcludedChart.js";
import { SourceChart } from "./charts/SourceChart.js";

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="card p-6">
      <h2 className="label mb-4">{title}</h2>
      {children}
    </section>
  );
}

export function Dashboard({
  data,
  reportId,
  meta,
}: {
  data: ReportData;
  reportId: string;
  meta?: { mode?: string; profileName?: string; createdAt?: string };
}) {
  const topNews = data.topNews ?? data.items ?? [];
  const trends = data.trendAnalysis ?? data.trends;
  const ts = data.technicalStats;
  const cached = ts.cachedItems ?? 0;
  const potential = data.potentiallyRelevant ?? [];
  const trendCount = trends.topTrends.length;
  const generated = meta?.createdAt
    ? new Date(meta.createdAt).toLocaleString("ru-RU")
    : new Date().toLocaleString("ru-RU");

  return (
    <div className="animate-rise space-y-10">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <span className="eyebrow">Intelligence Report</span>
          <h1 className="mt-3 text-2xl font-bold tracking-tight">
            {data.filename}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Collected: {data.totalFound} · Selected: {topNews.length} ·
            Potentially Relevant: {potential.length} · Trends: {trendCount}
          </p>
          <p className="mt-0.5 text-xs text-slate-400">Generated: {generated}</p>
          <div className="mt-3 flex flex-wrap items-center gap-1.5">
            {meta?.profileName && (
              <span className="rounded-full bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700 ring-1 ring-violet-100">
                ◆ {meta.profileName}
              </span>
            )}
            {meta?.mode && (
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                {meta.mode}
              </span>
            )}
            {data.selectedTopics?.map((t) => (
              <span
                key={t}
                className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-indigo-100"
              >
                {t}
              </span>
            ))}
          </div>
        </div>
        <ExportButtons reportId={reportId} />
      </div>

      <SummaryCards data={data} />

      {cached > 0 && (
        <div className="card flex flex-wrap items-center justify-between gap-4 border-emerald-100 bg-emerald-50/40 p-5">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
              ⚡
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-800">
                Кэш ускорил анализ
              </p>
              <p className="text-xs text-slate-500">
                {cached} из {cached + (ts.llmItems ?? 0)} статей взято из кэша —
                LLM не вызывался для них.
              </p>
            </div>
          </div>
          <p className="text-sm font-semibold text-emerald-700">
            ~{Math.round((ts.estTimeSavedMs ?? 0) / 1000)}с сэкономлено
          </p>
        </div>
      )}
      <ExecutiveSummary trends={trends} />
      <TrendsPanel trends={trends} />
      <StrategicSignals trends={trends} />

      {/* News */}
      <section>
        <h2 className="mb-4 text-lg font-bold tracking-tight">
          ТОП-{topNews.length} новостей
        </h2>
        {topNews.length === 0 ? (
          <div className="card p-10 text-center text-sm text-slate-400">
            Нет новостей для отображения — проверьте формат файла.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {topNews.map((item, i) => (
              <NewsCard key={i} item={item} rank={i + 1} reportId={reportId} mode="vote" />
            ))}
          </div>
        )}
      </section>

      {/* Potentially Relevant — discarded articles users can rescue */}
      {potential.length > 0 && (
        <section>
          <h2 className="mb-1 text-lg font-bold tracking-tight">Potentially Relevant</h2>
          <p className="mb-4 text-sm text-slate-500">
            High-scoring articles that didn’t make the TOP-{topNews.length}. Mark any
            the model missed.
          </p>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {potential.map((item, i) => (
              <NewsCard
                key={i}
                item={item}
                rank={topNews.length + i + 1}
                reportId={reportId}
                mode="rescue"
              />
            ))}
          </div>
        </section>
      )}

      {/* Charts */}
      <section>
        <h2 className="mb-4 text-lg font-bold tracking-tight">Аналитика</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <ChartCard title="Category Distribution">
            <CategoryChart data={data.categoryDistribution} />
          </ChartCard>
          <ChartCard title="Matched vs Excluded">
            <MatchedExcludedChart stats={data.processingStats} />
          </ChartCard>
          <ChartCard title="Exclusion Reasons">
            <ExclusionChart data={data.exclusionReasons} />
          </ChartCard>
          <ChartCard title="Source Distribution">
            <SourceChart data={data.sourceDistribution} />
          </ChartCard>
        </div>
      </section>

      <StatsPanel processing={data.processingStats} technical={data.technicalStats} />

      {/* Conclusion */}
      <section className="card relative overflow-hidden p-7">
        <div className="absolute -left-10 -top-10 h-32 w-32 rounded-full bg-gradient-to-br from-violet-100/50 to-indigo-100/40 blur-2xl" />
        <div className="relative">
          <span className="eyebrow">Аналитический вывод</span>
          <p className="mt-4 whitespace-pre-line text-[15px] leading-relaxed text-slate-700">
            {data.conclusion || "—"}
          </p>
        </div>
      </section>
    </div>
  );
}


# FILE: components/ErrorState.tsx

export function ErrorState({
  message,
  onReset,
}: {
  message: string;
  onReset: () => void;
}) {
  return (
    <div className="animate-rise mx-auto max-w-md">
      <div className="card p-8 text-center">
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-2xl text-rose-500 ring-1 ring-rose-100">
          ⚠
        </div>
        <h2 className="text-lg font-bold tracking-tight text-slate-800">
          Что-то пошло не так
        </h2>
        <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-slate-500">
          {message}
        </p>
        <button onClick={onReset} className="btn-primary mt-6">
          Начать заново
        </button>
      </div>
    </div>
  );
}


# FILE: components/ExecutiveSummary.tsx

import type { TrendAnalysis } from "../src/types/report.js";

export function ExecutiveSummary({ trends }: { trends: TrendAnalysis }) {
  return (
    <section className="card relative overflow-hidden p-7">
      <div className="absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br from-indigo-100/60 to-violet-100/40 blur-2xl" />
      <div className="relative">
        <span className="eyebrow">Executive Summary</span>
        <ol className="mt-5 space-y-3.5">
          {trends.executiveSummary.length === 0 ? (
            <li className="text-sm text-slate-400">—</li>
          ) : (
            trends.executiveSummary.map((c, i) => (
              <li key={i} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 text-xs font-bold text-white">
                  {i + 1}
                </span>
                <p className="text-[14px] leading-relaxed text-slate-700">{c}</p>
              </li>
            ))
          )}
        </ol>
      </div>
    </section>
  );
}


# FILE: components/ExportButtons.tsx

const EXPORTS: { fmt: string; label: string; primary?: boolean }[] = [
  { fmt: "markdown", label: "Markdown", primary: true },
  { fmt: "json", label: "JSON" },
  { fmt: "pdf", label: "PDF" },
  { fmt: "docx", label: "DOCX" },
];

/** Shared export bar — works for live dashboard, /run/[id], and history. */
export function ExportButtons({ reportId }: { reportId: string }) {
  return (
    <div className="flex flex-wrap gap-2">
      {EXPORTS.map((e) => (
        <a
          key={e.fmt}
          href={`/api/report/${reportId}/${e.fmt}`}
          className={e.primary ? "btn-primary" : "btn-ghost"}
        >
          {e.label}
        </a>
      ))}
    </div>
  );
}

