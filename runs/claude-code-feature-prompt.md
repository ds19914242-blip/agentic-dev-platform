You are a senior autonomous coding agent.

Feature request:
Add AI summaries to RSS feed items.

Repository:
/Users/danilsmetanev/Projects/rss-agent-lab_2

Relevant files:
- app/api/rss/collect/route.ts
- app/rss/page.tsx
- lib/rss/collect.ts
- lib/rss/fetchFeed.ts
- src/llm/client.ts
- src/agents/criteriaBatchAgent.ts
- src/agents/trendAnalysisAgent.ts

Task:
1. Analyze the provided files.
2. Identify the smallest safe implementation.
3. Modify the repository directly.
4. Prefer existing LLM utilities if available.
5. Run typecheck or tests if available.
6. Summarize changes and risks.

Rules:
- Do not modify auth, billing, secrets, or production config.
- Do not change database schema unless absolutely necessary.
- Keep changes small and reversible.

Context:


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


# FILE: app/rss/page.tsx

import { redirect } from "next/navigation";
export default function RssRedirect() {
  redirect("/sources");
}


# FILE: lib/rss/collect.ts

import { rssCollectionStorage, rssSourceStorage } from "../storage/index.js";
import { fetchFeed, type NormalizedArticle } from "./fetchFeed.js";
import {
  TELEGRAM_DEFAULT_MAX_POSTS,
  TELEGRAM_DEFAULT_WINDOW_DAYS,
  fetchTelegramChannel,
} from "../telegram/fetchTelegramChannel.js";

/**
 * Collect articles for a collection: fetch each ACTIVE source (RSS or Telegram),
 * aggregate, deduplicate, and update each source's last-fetch status. The
 * aggregated articles are serialized into the same "Новость #" text format the
 * existing deterministic parser understands — so the analysis pipeline is
 * reused with no engine changes, for both source types.
 */

export interface PerSourceResult {
  id: string;
  name: string;
  type: "rss" | "telegram";
  status: string;
  itemCount: number;
  error?: string;
}

export interface CollectStats {
  collectionId: string;
  collectionName: string;
  sourcesProcessed: number;
  rssProcessed: number;
  telegramProcessed: number;
  successful: number;
  failed: number;
  totalArticles: number;
  sampleHeadlines: string[];
  perSource: PerSourceResult[];
}

export interface CollectResult {
  ok: boolean;
  error?: string;
  stats?: CollectStats;
  /** Serialized .txt in the parser's expected format. */
  text?: string;
  fileName?: string;
}

function dedupe(articles: NormalizedArticle[]): NormalizedArticle[] {
  const seen = new Set<string>();
  const out: NormalizedArticle[] = [];
  for (const a of articles) {
    const key = (a.link || a.title).trim().toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(a);
  }
  return out;
}

/** Serialize to the labeled "Новость #" format (English labels). */
function serialize(articles: NormalizedArticle[]): string {
  return articles
    .map((a, i) => {
      const summary = a.summary.replace(/\s+/g, " ").trim();
      return [
        `Новость #${i + 1}`,
        `Дата (UTC): ${a.publishedAt || new Date().toISOString()}`,
        `Title: ${a.title}`,
        `Summary: ${summary}`,
        `Link: ${a.link}`,
      ].join("\n");
    })
    .join("\n\n");
}

export async function collectCollection(collectionId: string): Promise<CollectResult> {
  const collection = await rssCollectionStorage.get(collectionId);
  if (!collection) return { ok: false, error: "Collection not found." };

  const all = await Promise.all(
    collection.sourceIds.map((id) => rssSourceStorage.get(id)),
  );
  const sources = all.filter(
    (s): s is NonNullable<typeof s> => Boolean(s) && s!.isActive,
  );

  const perSource: PerSourceResult[] = [];
  const aggregated: NormalizedArticle[] = [];

  // Fetch sequentially to keep source-status writes simple and ordered.
  for (const src of sources) {
    const type = src.sourceType ?? "rss";
    let status: string;
    let itemCount: number;
    let error: string | undefined;

    if (type === "telegram" && src.telegram) {
      const res = await fetchTelegramChannel({
        channelUsername: src.telegram.channelUsername,
        maxPosts: src.telegram.maxPosts ?? TELEGRAM_DEFAULT_MAX_POSTS,
        timeWindowDays: src.telegram.timeWindowDays ?? TELEGRAM_DEFAULT_WINDOW_DAYS,
      });
      status = res.status;
      itemCount = res.itemCount;
      error = res.error;
      aggregated.push(...res.articles);
    } else {
      const res = await fetchFeed(src.url, src.name);
      status = res.status;
      itemCount = res.itemCount;
      error = res.error;
      aggregated.push(...res.articles);
    }

    perSource.push({ id: src.id, name: src.name, type, status, itemCount, error });
    await rssSourceStorage.update(src.id, {
      lastFetchedAt: new Date().toISOString(),
      lastStatus: status,
      lastError: error,
      lastItemCount: itemCount,
    });
  }

  const deduped = dedupe(aggregated);
  const stats: CollectStats = {
    collectionId: collection.id,
    collectionName: collection.name,
    sourcesProcessed: sources.length,
    rssProcessed: perSource.filter((p) => p.type === "rss").length,
    telegramProcessed: perSource.filter((p) => p.type === "telegram").length,
    successful: perSource.filter((p) => p.status === "ok").length,
    failed: perSource.filter((p) => p.status === "error").length,
    totalArticles: deduped.length,
    sampleHeadlines: deduped.slice(0, 5).map((a) => a.title),
    perSource,
  };

  return {
    ok: true,
    stats,
    text: serialize(deduped),
    fileName: `${collection.name}.collection`,
  };
}


# FILE: lib/rss/fetchFeed.ts

import Parser from "rss-parser";

/**
 * Fetch and normalize a single RSS/Atom feed. Robust to timeouts, invalid
 * feeds, and empty feeds — never throws (returns a status instead).
 */

export interface NormalizedArticle {
  title: string;
  link: string;
  summary: string;
  publishedAt: string;
  sourceName: string;
}

export type FeedStatus = "ok" | "empty" | "error";

export interface FetchFeedResult {
  ok: boolean;
  status: FeedStatus;
  itemCount: number;
  error?: string;
  articles: NormalizedArticle[];
}

const parser = new Parser({
  timeout: 10_000,
  headers: { "User-Agent": "rss-agent-lab/1.0 (+workspace)" },
});

export async function fetchFeed(
  url: string,
  sourceName = "",
): Promise<FetchFeedResult> {
  try {
    const feed = await parser.parseURL(url);
    const articles: NormalizedArticle[] = (feed.items ?? []).map((item) => ({
      title: (item.title ?? "").trim(),
      link: (item.link ?? "").trim(),
      summary: (
        (item as { "content:encoded"?: string })["content:encoded"] ??
        item.contentSnippet ??
        item.content ??
        item.summary ??
        ""
      ).trim(),
      publishedAt: (item.isoDate ?? item.pubDate ?? "").trim(),
      sourceName: sourceName || feed.title || "",
    }));

    if (articles.length === 0) {
      return { ok: true, status: "empty", itemCount: 0, articles: [] };
    }
    return { ok: true, status: "ok", itemCount: articles.length, articles };
  } catch (err) {
    return {
      ok: false,
      status: "error",
      itemCount: 0,
      error: err instanceof Error ? err.message : String(err),
      articles: [],
    };
  }
}


# FILE: src/llm/client.ts

import Anthropic from "@anthropic-ai/sdk";

/**
 * Shared Anthropic client. Reads ANTHROPIC_API_KEY from the environment
 * (load it via `import "dotenv/config"` in the entry point before use).
 *
 * `maxRetries` covers transient 429/5xx with exponential backoff; the agents
 * add their own bounded retry on top for schema/refusal misses.
 */
export const anthropic = new Anthropic({ maxRetries: 4 });

/**
 * Model for the report workflow. Overridable via ANTHROPIC_MODEL; defaults to
 * Sonnet 4.6 (reasoning at lower cost).
 */
export const MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-4-6";


# FILE: src/agents/criteriaBatchAgent.ts

import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { anthropic, MODEL } from "../llm/client.js";
import { recordUsage } from "../metrics/runMetrics.js";
import {
  DEFAULT_CRITERIA,
  resolveKeywords,
  type AnalysisCriteria,
} from "../analysis/criteria.js";
import type { FilterResult, RssTextArticle } from "../types/report.js";

const AnalysisSchema = z.object({
  index: z.number().int(),
  matchesCriteria: z.boolean(),
  relevanceScore: z.number().int().min(1).max(10),
  categories: z.array(z.string()),
  reason: z.string(),
  shortDescriptionRu: z.string(),
});
const BatchSchema = z.object({ analyses: z.array(AnalysisSchema) });

/** Build the rubric from the user's selected topics + keyword lists. */
function buildSystemPrompt(criteria: AnalysisCriteria): string {
  const { include, exclude } = resolveKeywords(criteria);
  const topics =
    criteria.selectedTopics.length > 0
      ? criteria.selectedTopics.join(", ")
      : "общие технологические и рыночные темы";

  return `Ты — аналитик новостей по информационной безопасности и технологиям.
Тебе дают МАССИВ новостей с числовыми индексами. Проанализируй КАЖДУЮ и верни
массив "analyses" — ровно по одному объекту на каждую новость, с тем же index.

Заказчик выбрал темы интереса: ${topics}.

ИНТЕРЕСНО (matchesCriteria = true, выше relevanceScore) — новости по этим темам
и ключевым словам: ${include.join(", ")}.

НЕ ИНТЕРЕСНО (matchesCriteria = false, низкий relevanceScore) — новости про:
${exclude.join(", ")}, а также нерелевантный IT-шум.

Для каждой новости:
- index: тот же индекс, что во входных данных.
- relevanceScore: 1-10 (10 = максимально по выбранным темам заказчика).
- categories: 1-3 короткие темы (по возможности из списка выбранных тем).
- reason: одно предложение.
- shortDescriptionRu: 2-3 предложения, нейтральное описание на русском.`;
}

/**
 * Analyze a batch of articles in ONE Claude call. Returns FilterResult[]
 * aligned to the input order; any index the model omits gets a safe default.
 */
export async function criteriaBatchAgent(
  articles: RssTextArticle[],
  criteria: AnalysisCriteria = DEFAULT_CRITERIA,
): Promise<FilterResult[]> {
  const systemPrompt = buildSystemPrompt(criteria);
  const input = articles.map((a, i) => ({
    index: i + 1,
    title: a.title,
    date: a.date,
    summary: a.summary,
  }));

  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await anthropic.messages.parse({
        model: MODEL,
        max_tokens: 8000,
        thinking: { type: "disabled" },
        system: [
          { type: "text", text: systemPrompt, cache_control: { type: "ephemeral" } },
        ],
        output_config: { effort: "low", format: zodOutputFormat(BatchSchema) },
        messages: [
          {
            role: "user",
            content: `Новости для анализа (JSON):\n${JSON.stringify(input, null, 2)}`,
          },
        ],
      });
      recordUsage(response.usage);

      if (response.parsed_output) {
        return alignByIndex(response.parsed_output.analyses, articles);
      }
      lastErr = new Error("empty parsed_output");
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr;
}

/** Map model results back to input order by index; fill gaps with defaults. */
function alignByIndex(
  analyses: z.infer<typeof BatchSchema>["analyses"],
  articles: RssTextArticle[],
): FilterResult[] {
  const byIndex = new Map(analyses.map((a) => [a.index, a]));
  return articles.map((article, i) => {
    const a = byIndex.get(i + 1);
    if (!a) return defaultFilter(article);
    return {
      matchesCriteria: a.matchesCriteria,
      relevanceScore: a.relevanceScore,
      categories: a.categories,
      reason: a.reason,
      shortDescriptionRu: a.shortDescriptionRu,
    };
  });
}

/** Conservative fallback when the model didn't analyze an article. */
export function defaultFilter(article: RssTextArticle): FilterResult {
  return {
    matchesCriteria: false,
    relevanceScore: 1,
    categories: [],
    reason: "анализ недоступен",
    shortDescriptionRu: article.summary.slice(0, 300),
  };
}


# FILE: src/agents/trendAnalysisAgent.ts

import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { anthropic, MODEL } from "../llm/client.js";
import { recordUsage } from "../metrics/runMetrics.js";
import { DEFAULT_CRITERIA, type AnalysisCriteria } from "../analysis/criteria.js";
import type { RankedArticle, TrendAnalysis } from "../types/report.js";

const TrendSchema = z.object({
  executiveSummary: z.array(z.string()),
  topTrends: z.array(
    z.object({
      name: z.string(),
      explanation: z.string(),
      supportingTitles: z.array(z.string()),
      confidence: z.enum(["Low", "Medium", "High"]),
    }),
  ),
  strategicSignals: z.object({
    productLaunches: z.array(z.string()),
    partnershipsIntegrations: z.array(z.string()),
    aiInitiatives: z.array(z.string()),
    iamGovernance: z.array(z.string()),
    secOpsPlatform: z.array(z.string()),
  }),
  marketOutlook: z.string(),
});

function buildSystemPrompt(criteria: AnalysisCriteria, short: boolean): string {
  const focus =
    criteria.selectedTopics.length > 0
      ? `Заказчик выбрал темы интереса: ${criteria.selectedTopics.join(", ")}. ` +
        `Сфокусируй выводы и тренды на этих темах.\n\n`
      : "";

  if (short) {
    return `Ты — рыночный аналитик по кибербезопасности и технологиям.
${focus}На вход — СТРУКТУРИРОВАННЫЙ список TOP-N новостей. Дай КРАТКУЮ аналитику
на русском строго в JSON:

1. executiveSummary: 3 кратких ключевых вывода.
2. topTrends: 3 главных тренда (name, краткий explanation, supportingTitles
   ДОСЛОВНО из набора, confidence Low|Medium|High).
3. strategicSignals: распредели заголовки по группам productLaunches,
   partnershipsIntegrations, aiInitiatives, iamGovernance, secOpsPlatform.
4. marketOutlook: 1-2 коротких абзаца.

Используй только предоставленные заголовки. Не выдумывай новости.`;
  }

  return `Ты — старший рыночный аналитик по кибербезопасности и технологиям.
${focus}На вход ты получаешь СТРУКТУРИРОВАННЫЙ список из TOP-N новостей (заголовки,
оценки релевантности, категории) — НЕ сырой текст. На его основе подготовь
аналитику на русском языке строго в JSON:

1. executiveSummary: ровно 5 ключевых выводов о рынке.
2. topTrends: ровно 5 трендов. Для каждого:
   - name: краткое название тренда;
   - explanation: объяснение;
   - supportingTitles: точные заголовки из набора, подтверждающие тренд
     (используй заголовки ДОСЛОВНО, не выдумывай);
   - confidence: Low | Medium | High.
3. strategicSignals: распредели релевантные заголовки по группам:
   productLaunches, partnershipsIntegrations, aiInitiatives, iamGovernance,
   secOpsPlatform.
4. marketOutlook: 3-5 абзацев — куда движется рынок, на что обратить внимание
   лидерам безопасности, самый сильный сигнал из набора.

Используй только предоставленные заголовки. Не выдумывай новости.`;
}

/**
 * Run the Trend Analysis Agent over the selected TOP-N (structured fields
 * only — never raw text). Supporting titles are validated against the actual
 * dataset and counts are derived deterministically, so the output is auditable.
 * `short` produces a lighter, cheaper analysis (Fast mode).
 */
export async function trendAnalysisAgent(
  selected: RankedArticle[],
  criteria: AnalysisCriteria = DEFAULT_CRITERIA,
  opts: { short?: boolean } = {},
): Promise<TrendAnalysis> {
  const short = opts.short ?? false;
  const systemPrompt = buildSystemPrompt(criteria, short);
  const digest = selected.map((r) => ({
    title: r.article.title,
    score: r.filter.relevanceScore,
    categories: r.filter.categories,
    matchesCriteria: !r.isBackfill,
  }));

  const validTitles = new Set(
    selected.map((r) => r.article.title.trim().toLowerCase()),
  );

  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await anthropic.messages.parse({
        model: MODEL,
        max_tokens: short ? 2000 : 4000,
        thinking: { type: "disabled" },
        system: [
          { type: "text", text: systemPrompt, cache_control: { type: "ephemeral" } },
        ],
        output_config: { effort: "low", format: zodOutputFormat(TrendSchema) },
        messages: [
          {
            role: "user",
            content: `TOP-25 (JSON):\n${JSON.stringify(digest, null, 2)}`,
          },
        ],
      });
      recordUsage(response.usage);

      if (response.parsed_output) {
        return normalize(response.parsed_output, validTitles);
      }
      lastErr = new Error("empty parsed_output");
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr;
}

/** Drop fabricated supporting titles and derive supportingCount from them. */
function normalize(
  out: z.infer<typeof TrendSchema>,
  validTitles: Set<string>,
): TrendAnalysis {
  const keepReal = (titles: string[]) =>
    titles.filter((t) => validTitles.has(t.trim().toLowerCase()));

  return {
    executiveSummary: out.executiveSummary,
    topTrends: out.topTrends.map((t) => {
      const supportingTitles = keepReal(t.supportingTitles);
      return { ...t, supportingTitles, supportingCount: supportingTitles.length };
    }),
    strategicSignals: {
      productLaunches: keepReal(out.strategicSignals.productLaunches),
      partnershipsIntegrations: keepReal(out.strategicSignals.partnershipsIntegrations),
      aiInitiatives: keepReal(out.strategicSignals.aiInitiatives),
      iamGovernance: keepReal(out.strategicSignals.iamGovernance),
      secOpsPlatform: keepReal(out.strategicSignals.secOpsPlatform),
    },
    marketOutlook: out.marketOutlook,
  };
}

