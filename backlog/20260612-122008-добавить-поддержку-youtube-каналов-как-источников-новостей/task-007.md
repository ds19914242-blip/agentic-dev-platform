Type: audit_task
Pipeline: audit
Risk: medium
Status: done_no_pr

### Task 007 — End-to-end manual QA pass

**Goal:** Run the manual verification scenarios end-to-end and tighten error messages/edge-case handling.
**Scope:** Execute all 10 manual verification scenarios (add by channel URL, `@handle`, raw `channel_id`; invalid input; empty channel; volume limits; edit & persist; deactivate/delete; mixed RSS+Telegram+Reddit+YouTube collection; backward compatibility for sources with no `sourceType`). File or fix any gaps in error messaging and edge-case handling (live/upcoming/Shorts dates, empty/long descriptions, video/feed-URL misuse). No new infrastructure.
**Suggested files:** _verification only — touch points across `lib/youtube/fetchYouTubeChannel.ts`, `lib/rss/collect.ts`, the API routes, and `app/sources/page.tsx` as defects surface._
**Acceptance criteria:** All 10 scenarios pass; invalid input shows clear errors in both Test and Save; empty channel handled as `empty`; mixed collections aggregate all four types; pre-`sourceType` sources still collect as RSS; no TypeScript errors.
**Risk:** medium

## Depends On

task-003, task-006
