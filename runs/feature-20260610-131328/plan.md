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
