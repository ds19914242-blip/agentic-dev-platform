# Feature Request

Add article source filtering by domain

# Repository

/Users/danilsmetanev/Projects/rss-agent-lab_2

# Affected Files

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

# Task

You are a senior autonomous coding agent.

Analyze the affected files and create a detailed implementation plan. Do not modify files yet.

Rules:
- First explain what already exists.
- Then create an implementation plan.
- Do not modify auth, billing, secrets, database schema, or deployment config unless explicitly required.
- Keep changes small and reversible.
- Do not run implementation yet. Stop after the plan.
- Summarize changed files and risks.

# Context



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


# FILE: src/agents/summaryBatchAgent.ts

import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { anthropic, MODEL } from "../llm/client.js";
import { recordUsage } from "../metrics/runMetrics.js";
import type { RssTextArticle } from "../types/report.js";

const SummarySchema = z.object({
  index: z.number().int(),
  summaryRu: z.string(),
});
const BatchSchema = z.object({ summaries: z.array(SummarySchema) });

/** One AI summary aligned to a preview article by its `number`. */
export interface ArticleSummary {
  number: number;
  summaryRu: string;
}

const SYSTEM_PROMPT = `Ты — редактор новостей по технологиям и информационной
безопасности. Тебе дают МАССИВ новостей с числовыми индексами. Для КАЖДОЙ верни
объект в массиве "summaries" — ровно по одному на каждую новость, с тем же index.

Для каждой новости:
- index: тот же индекс, что во входных данных.
- summaryRu: нейтральное краткое описание на русском, 2-3 предложения. Только суть,
  без оценок и без релевантности.`;

/**
 * Summarize a small batch of articles in ONE Claude call — criteria-free,
 * summary-only. Mirrors criteriaBatchAgent's structured-output + retry pattern.
 * Returns summaries aligned to each input article's `number`; any index the
 * model omits falls back to the article's original summary.
 */
export async function summaryBatchAgent(
  articles: RssTextArticle[],
): Promise<ArticleSummary[]> {
  const input = articles.map((a, i) => ({
    index: i + 1,
    title: a.title,
    summary: a.summary,
  }));

  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await anthropic.messages.parse({
        model: MODEL,
        max_tokens: 3000,
        thinking: { type: "disabled" },
        system: [
          { type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } },
        ],
        output_config: { effort: "low", format: zodOutputFormat(BatchSchema) },
        messages: [
          {
            role: "user",
            content: `Новости для краткого описания (JSON):\n${JSON.stringify(input, null, 2)}`,
          },
        ],
      });
      recordUsage(response.usage);

      if (response.parsed_output) {
        return alignByIndex(response.parsed_output.summaries, articles);
      }
      lastErr = new Error("empty parsed_output");
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr;
}

/** Map model results back to input order by index; fill gaps with the raw summary. */
function alignByIndex(
  summaries: z.infer<typeof BatchSchema>["summaries"],
  articles: RssTextArticle[],
): ArticleSummary[] {
  const byIndex = new Map(summaries.map((s) => [s.index, s]));
  return articles.map((article, i) => {
    const s = byIndex.get(i + 1);
    return {
      number: article.number,
      summaryRu: s?.summaryRu || article.summary.slice(0, 300),
    };
  });
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


# FILE: src/analysis/criteria.ts

/**
 * Analysis criteria: topics + keywords + topN. Owns the topic→keyword mapping
 * and the defaults. Threaded into the prefilter and both LLM agents so the
 * report reflects the user's selected topics.
 */

import { isPerformanceMode, type PerformanceMode } from "./performance.js";

export interface AnalysisCriteria {
  /** Selected topic labels (from TOPIC_KEYWORDS keys). */
  selectedTopics: string[];
  /** Extra interest keywords typed by the user (extend topic keywords). */
  includeKeywords: string[];
  /** Exclude keywords (negative signal). */
  excludeKeywords: string[];
  /** Number of items in the final report. */
  topN: number;
  /** Performance mode (web UI). Undefined → CLI/env defaults. */
  performanceMode?: PerformanceMode;
}

/** Topic label → the keywords it contributes to the interest signal. */
export const TOPIC_KEYWORDS: Record<string, string[]> = {
  AI: ["AI", "artificial intelligence"],
  CyberSec: ["cybersecurity", "infosec", "cyber"],
  IAM: ["IAM", "identity", "access management"],
  SecOps: ["SecOps", "SOC", "security operations"],
  Governance: ["governance", "GRC", "oversight"],
  "Product Releases": ["product launch", "release", "launch", "product"],
  Partnerships: ["partnership", "integration", "acquisition", "funding", "alliance"],
  "Market Trends": ["market", "trend", "strategy", "investment"],
  "Cloud Security": ["cloud security", "CSPM", "CNAPP", "cloud"],
  "Data Security": ["data security", "DLP", "encryption"],
  Privacy: ["privacy", "data protection", "PII"],
  Compliance: ["compliance", "regulatory", "audit"],
  "Digital Identity": ["digital identity", "authentication", "verification"],
  "Agentic AI": ["agentic", "agents", "autonomous agent"],
  "LLM / GenAI": ["LLM", "GenAI", "generative AI", "MCP"],
  "Security Platforms": ["platform", "security platform"],
};

/** All topic labels, in display order. */
export const ALL_TOPICS = Object.keys(TOPIC_KEYWORDS);

/** Original interest list — keeps CLI/report:json behavior identical. */
const DEFAULT_INCLUDE_KEYWORDS = [
  "AI", "artificial intelligence", "agentic", "agents", "LLM", "MCP",
  "identity", "IAM", "access management", "governance", "GRC", "SecOps",
  "SOC", "platform", "product launch", "release", "integration",
  "partnership", "acquisition", "funding", "market", "strategy",
  "digital security", "cloud security",
];

/** Original exclude list. */
export const DEFAULT_EXCLUDE_KEYWORDS = [
  "CVE", "vulnerability", "exploit", "malware", "ransomware", "trojan",
  "botnet", "phishing", "attack", "breach", "incident", "zero-day",
  "patch", "virus", "hardware", "telecom",
];

/**
 * Backend default criteria (used by the CLI and when no criteria is supplied).
 * selectedTopics is empty so resolveKeywords() returns exactly the original
 * interest list — preserving prior behavior precisely.
 */
export const DEFAULT_CRITERIA: AnalysisCriteria = {
  selectedTopics: [],
  includeKeywords: DEFAULT_INCLUDE_KEYWORDS,
  excludeKeywords: DEFAULT_EXCLUDE_KEYWORDS,
  topN: 25,
};

/** Web UI defaults (the preview screen pre-selects these). */
export const WEB_DEFAULT_TOPICS = [
  "AI", "CyberSec", "IAM", "SecOps", "Governance",
  "Product Releases", "Market Trends",
];
export const WEB_DEFAULT_EXCLUDE = [
  "CVE", "vulnerability", "malware", "ransomware", "exploit", "attack",
  "breach", "incident", "virus", "hardware", "telecom",
];

/**
 * Resolve criteria into effective include/exclude keyword lists.
 * include = ∪(keywords of selected topics) ∪ custom include keywords (extend).
 */
export function resolveKeywords(criteria: AnalysisCriteria): {
  include: string[];
  exclude: string[];
} {
  const include = new Set<string>();
  for (const topic of criteria.selectedTopics) {
    for (const kw of TOPIC_KEYWORDS[topic] ?? []) include.add(kw);
  }
  for (const kw of criteria.includeKeywords) {
    const t = kw.trim();
    if (t) include.add(t);
  }
  const exclude = criteria.excludeKeywords
    .map((k) => k.trim())
    .filter((k) => k.length > 0);

  return { include: [...include], exclude };
}

/** Normalize a partial criteria payload (from the API) into a full object. */
export function normalizeCriteria(input: Partial<AnalysisCriteria>): AnalysisCriteria {
  const topN = Number(input.topN);
  return {
    selectedTopics: Array.isArray(input.selectedTopics) ? input.selectedTopics : [],
    includeKeywords: Array.isArray(input.includeKeywords) ? input.includeKeywords : [],
    excludeKeywords: Array.isArray(input.excludeKeywords)
      ? input.excludeKeywords
      : DEFAULT_EXCLUDE_KEYWORDS,
    topN: Number.isFinite(topN) && topN > 0 ? Math.floor(topN) : 25,
    performanceMode: isPerformanceMode(input.performanceMode)
      ? input.performanceMode
      : "balanced",
  };
}


# FILE: src/analysis/feedbackRanking.ts

import type { Feedback } from "../../lib/storage/types.js";
import type { FeedbackInfluence } from "../../lib/storage/types.js";
import type { RankedArticle } from "../types/report.js";

/**
 * Lightweight, rule-based, explainable feedback ranking. NO ML, no retraining.
 * Produces a small additive score adjustment per article from prior votes:
 *
 *  - Source affinity: source with net-positive votes → boost; net-negative → penalty.
 *  - Topic affinity: categories the user tends to mark relevant → small boost.
 *  - "missed_but_relevant" counts as a strong positive signal for its source/topics.
 *
 * The adjustment is scaled by the Feedback Influence setting and applied as a
 * stable re-sort. When influence is "off" or there is no feedback, this is a
 * no-op — the analysis engine, prompts, prefilter, cache, and LLM are untouched.
 */

const INFLUENCE_WEIGHT: Record<FeedbackInfluence, number> = {
  off: 0,
  low: 0.5,
  medium: 1,
  high: 2,
};

interface Affinity {
  bySource: Map<string, number>;
  byCategory: Map<string, number>;
}

function hostOf(link: string): string {
  try {
    return new URL(link).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

/** Build per-source and per-category affinity tallies from feedback. */
function buildAffinity(feedback: Feedback[]): Affinity {
  const bySource = new Map<string, number>();
  const byCategory = new Map<string, number>();
  const add = (map: Map<string, number>, key: string, delta: number) => {
    if (!key) return;
    map.set(key, (map.get(key) ?? 0) + delta);
  };
  for (const f of feedback) {
    const delta =
      f.vote === "relevant" ? 1 : f.vote === "not_relevant" ? -1 : f.vote === "missed_but_relevant" ? 2 : 0;
    if (f.source) add(bySource, f.source, delta);
    for (const c of f.categories ?? []) add(byCategory, c, delta);
  }
  return { bySource, byCategory };
}

/** Clamp helper. */
function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v));
}

/**
 * Re-rank articles by (relevanceScore + feedbackAdjustment). Returns a NEW array
 * sorted desc; ties keep original article-number order for stability. Articles
 * are not mutated. Returns the input order unchanged when influence is off or no
 * feedback exists.
 */
export function applyFeedbackRanking(
  articles: RankedArticle[],
  feedback: Feedback[],
  influence: FeedbackInfluence,
): RankedArticle[] {
  const weight = INFLUENCE_WEIGHT[influence] ?? 0;
  if (weight === 0 || feedback.length === 0) return articles;

  const aff = buildAffinity(feedback);

  const adjusted = articles.map((r) => {
    const host = hostOf(r.article.link);
    // Source affinity: net votes → small bounded boost/penalty.
    const sourceSignal = clamp((aff.bySource.get(host) ?? 0) * 0.25, -1.5, 1.5);
    // Topic affinity: average category signal → smaller bounded boost.
    const cats = r.filter.categories ?? [];
    const catSignal =
      cats.length > 0
        ? clamp(
            (cats.reduce((s, c) => s + (aff.byCategory.get(c) ?? 0), 0) / cats.length) * 0.15,
            -1,
            1,
          )
        : 0;
    const adjustment = (sourceSignal + catSignal) * weight;
    return { r, adjusted: r.filter.relevanceScore + adjustment };
  });

  return adjusted
    .sort((a, b) => b.adjusted - a.adjusted || a.r.article.number - b.r.article.number)
    .map((x) => x.r);
}


# FILE: src/analysis/performance.ts

/**
 * Performance modes — tune speed vs depth. Selected in the web UI; the CLI
 * leaves `performanceMode` undefined and falls back to env-based settings.
 */

export type PerformanceMode = "fast" | "balanced" | "deep";
export type TrendDepth = "short" | "full";

export interface PerformanceSettings {
  maxCandidates: number;
  batchSize: number;
  concurrency: number;
  trendDepth: TrendDepth;
}

export const PERFORMANCE_PRESETS: Record<PerformanceMode, PerformanceSettings> = {
  fast: { maxCandidates: 50, batchSize: 10, concurrency: 3, trendDepth: "short" },
  balanced: { maxCandidates: 150, batchSize: 20, concurrency: 3, trendDepth: "full" },
  deep: { maxCandidates: 300, batchSize: 20, concurrency: 2, trendDepth: "full" },
};

export const PERFORMANCE_MODES: PerformanceMode[] = ["fast", "balanced", "deep"];

/** Resolve a preset for a known mode, or undefined to fall back to env. */
export function resolvePerformance(
  mode: PerformanceMode | undefined,
): PerformanceSettings | undefined {
  return mode ? PERFORMANCE_PRESETS[mode] : undefined;
}

export function isPerformanceMode(v: unknown): v is PerformanceMode {
  return v === "fast" || v === "balanced" || v === "deep";
}


# FILE: src/analysis/profiles.ts

import type { Profile } from "../../lib/storage/types.js";

/**
 * Built-in topic profiles. Pre-fill topics/keywords/TOP-N/mode on the
 * configure screen. These cannot be edited destructively or deleted.
 */
export const BUILTIN_PROFILES: Profile[] = [
  {
    id: "builtin-ai-security",
    name: "AI Security",
    description: "AI/ML security, agentic systems, LLM and GenAI risk.",
    selectedTopics: ["AI", "Agentic AI", "LLM / GenAI", "CyberSec", "Data Security"],
    includeKeywords: ["AI security", "model security", "prompt injection"],
    excludeKeywords: ["CVE", "malware", "ransomware", "hardware"],
    defaultTopN: 25,
    defaultMode: "balanced",
    builtIn: true,
  },
  {
    id: "builtin-iam-market",
    name: "IAM Market",
    description: "Identity, access management, and digital identity market moves.",
    selectedTopics: ["IAM", "Digital Identity", "Governance", "Market Trends"],
    includeKeywords: ["IAM", "identity", "access management", "SSO", "MFA"],
    excludeKeywords: ["CVE", "malware", "ransomware", "telecom"],
    defaultTopN: 25,
    defaultMode: "balanced",
    builtIn: true,
  },
  {
    id: "builtin-secops-platforms",
    name: "SecOps Platforms",
    description: "Security operations, SOC, and platform consolidation.",
    selectedTopics: ["SecOps", "Security Platforms", "Cloud Security", "Product Releases"],
    includeKeywords: ["SecOps", "SOC", "SIEM", "SOAR", "XDR", "platform"],
    excludeKeywords: ["CVE", "malware", "attack", "incident"],
    defaultTopN: 25,
    defaultMode: "balanced",
    builtIn: true,
  },
  {
    id: "builtin-agentic-ai",
    name: "Agentic AI",
    description: "Autonomous agents, agent frameworks, and agentic workflows.",
    selectedTopics: ["Agentic AI", "AI", "LLM / GenAI", "Product Releases"],
    includeKeywords: ["agentic", "agents", "autonomous", "MCP", "orchestration"],
    excludeKeywords: ["CVE", "malware", "ransomware", "hardware"],
    defaultTopN: 25,
    defaultMode: "deep",
    builtIn: true,
  },
  {
    id: "builtin-vendor-radar",
    name: "Vendor Radar",
    description: "Product launches, partnerships, funding, and M&A across vendors.",
    selectedTopics: ["Product Releases", "Partnerships", "Market Trends", "Security Platforms"],
    includeKeywords: ["launch", "release", "partnership", "acquisition", "funding", "integration"],
    excludeKeywords: ["CVE", "vulnerability", "malware", "attack"],
    defaultTopN: 30,
    defaultMode: "balanced",
    builtIn: true,
  },
  {
    id: "builtin-governance-compliance",
    name: "Governance & Compliance",
    description: "Regulation, governance, GRC, privacy, and compliance.",
    selectedTopics: ["Governance", "Compliance", "Privacy", "Data Security"],
    includeKeywords: ["governance", "compliance", "regulation", "GDPR", "privacy", "audit"],
    excludeKeywords: ["CVE", "malware", "ransomware", "hardware"],
    defaultTopN: 25,
    defaultMode: "balanced",
    builtIn: true,
  },
];


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


# Import Map

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


# Agent Context

# Agent Context

## architecture_review

# Architecture Review

## Feature Request

Add article source filtering by domain

## Planner Input

# Implementation Plan

## Feature Request

Add article source filtering by domain

## Affected Files

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

## Plan

1. Review affected files.
2. Identify existing functionality.
3. Define the smallest safe implementation.
4. Modify only necessary files.
5. Run typecheck or tests.
6. Review git diff.
7. Summarize changes and risks.

## Safety Rules

- Do not modify auth.
- Do not modify billing.
- Do not modify secrets.
- Do not modify database schema unless explicitly required.
- Do not modify deployment configuration.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Agent/LLM layer: src/agents/criteriaBatchAgent.ts
- Agent/LLM layer: src/agents/summaryBatchAgent.ts
- Agent/LLM layer: src/agents/trendAnalysisAgent.ts
- Other: src/analysis/criteria.ts
- Other: src/analysis/feedbackRanking.ts
- Other: src/analysis/performance.ts
- Other: src/analysis/profiles.ts
- LLM client layer: src/llm/client.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.


## plan

# Implementation Plan

## Feature Request

Add article source filtering by domain

## Affected Files

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

## Plan

1. Review affected files.
2. Identify existing functionality.
3. Define the smallest safe implementation.
4. Modify only necessary files.
5. Run typecheck or tests.
6. Review git diff.
7. Summarize changes and risks.

## Safety Rules

- Do not modify auth.
- Do not modify billing.
- Do not modify secrets.
- Do not modify database schema unless explicitly required.
- Do not modify deployment configuration.


## qa_plan

# QA Plan

## Feature Request

Add article source filtering by domain

## Based On Plan

# Implementation Plan

## Feature Request

Add article source filtering by domain

## Affected Files

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

## Plan

1. Review affected files.
2. Identify existing functionality.
3. Define the smallest safe implementation.
4. Modify only necessary files.
5. Run typecheck or tests.
6. Review git diff.
7. Summarize changes and risks.

## Safety Rules

- Do not modify auth.
- Do not modify billing.
- Do not modify secrets.
- Do not modify database schema unless explicitly required.
- Do not modify deployment configuration.


## Based On Architecture Review

# Architecture Review

## Feature Request

Add article source filtering by domain

## Planner Input

# Implementation Plan

## Feature Request

Add article source filtering by domain

## Affected Files

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

## Plan

1. Review affected files.
2. Identify existing functionality.
3. Define the smallest safe implementation.
4. Modify only necessary files.
5. Run typecheck or tests.
6. Review git diff.
7. Summarize changes and risks.

## Safety Rules

- Do not modify auth.
- Do not modify billing.
- Do not modify secrets.
- Do not modify database schema unless explicitly required.
- Do not modify deployment configuration.


## Review Focus

- Does the plan fit existing architecture?
- Which modules are affected?
- Are there unnecessary risky changes?
- Are auth, billing, secrets, DB schema or deployment config affected?

## Affected Areas

- Agent/LLM layer: src/agents/criteriaBatchAgent.ts
- Agent/LLM layer: src/agents/summaryBatchAgent.ts
- Agent/LLM layer: src/agents/trendAnalysisAgent.ts
- Other: src/analysis/criteria.ts
- Other: src/analysis/feedbackRanking.ts
- Other: src/analysis/performance.ts
- Other: src/analysis/profiles.ts
- LLM client layer: src/llm/client.ts

## Architecture Recommendation

Reuse existing modules where possible.
Avoid new infrastructure unless explicitly required.
Keep implementation small and reversible.


## Validation Goals

- Confirm the feature works as requested.
- Confirm the implementation follows the plan.
- Confirm architecture risks were addressed.
- Confirm existing flows still work.
- Confirm no unsafe areas were modified.

## Suggested Checks

- Run typecheck.
- Review git diff.
- Manually verify the changed UI/API flow.
- Check error state if API/LLM call fails.

## Affected Files To Review

- src/agents/criteriaBatchAgent.ts
- src/agents/summaryBatchAgent.ts
- src/agents/trendAnalysisAgent.ts
- src/analysis/criteria.ts
- src/analysis/feedbackRanking.ts
- src/analysis/performance.ts
- src/analysis/profiles.ts
- src/llm/client.ts

## Required Command

```bash
npx tsc --noEmit
```

