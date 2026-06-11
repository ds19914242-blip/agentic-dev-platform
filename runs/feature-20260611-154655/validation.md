# Validation Result

## Overall Result

passed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: passed

Timed Out: False

Exit Code: 0

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build

  ▲ Next.js 14.2.35

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
[storage] DATABASE_URL present: no
[storage] selected backend: local-fs
   Generating static pages (0/19) ...
   Generating static pages (4/19) 
   Generating static pages (9/19) 
   Generating static pages (14/19) 
 ✓ Generating static pages (19/19)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    6.29 kB         214 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ƒ /api/analyze                         0 B                0 B
├ ƒ /api/auth/login                      0 B                0 B
├ ƒ /api/auth/logout                     0 B                0 B
├ ƒ /api/benchmark                       0 B                0 B
├ ƒ /api/favorites                       0 B                0 B
├ ƒ /api/favorites/[id]                  0 B                0 B
├ ƒ /api/feedback                        0 B                0 B
├ ƒ /api/health                          0 B                0 B
├ ƒ /api/health/db                       0 B                0 B
├ ƒ /api/jobs/[jobId]                    0 B                0 B
├ ƒ /api/overview                        0 B                0 B
├ ƒ /api/profiles                        0 B                0 B
├ ƒ /api/profiles/[id]                   0 B                0 B
├ ƒ /api/report/[id]/docx                0 B                0 B
├ ƒ /api/report/[id]/json                0 B                0 B
├ ƒ /api/report/[id]/markdown            0 B                0 B
├ ƒ /api/report/[id]/pdf                 0 B                0 B
├ ƒ /api/rss/collect                     0 B                0 B
├ ƒ /api/rss/collections                 0 B                0 B
├ ƒ /api/rss/collections/[id]            0 B                0 B
├ ƒ /api/rss/sources                     0 B                0 B
├ ƒ /api/rss/sources/[id]                0 B                0 B
├ ƒ /api/rss/summarize                   0 B                0 B
├ ƒ /api/rss/test                        0 B                0 B
├ ƒ /api/runs                            0 B                0 B
├ ƒ /api/runs/[id]                       0 B                0 B
├ ƒ /api/settings                        0 B                0 B
├ ƒ /api/upload                          0 B                0 B
├ ○ /benchmark                           2.5 kB         92.6 kB
├ ○ /collections                         3.21 kB        90.5 kB
├ ○ /dashboard                           1.61 kB        97.7 kB
├ ○ /feedback                            1.55 kB        88.9 kB
├ ○ /history                             152 B          87.5 kB
├ ○ /login                               1.41 kB        88.7 kB
├ ○ /profiles                            3.22 kB        90.5 kB
├ ○ /reading-list                        1.81 kB        89.1 kB
├ ○ /reports                             2.63 kB        98.7 kB
├ ○ /rss                                 152 B          87.5 kB
├ ○ /rss/collections                     152 B          87.5 kB
├ ƒ /run/[id]                            936 B           214 kB
├ ○ /settings                            1.7 kB           89 kB
├ ○ /sources                             7.68 kB          95 kB
├ ○ /templates                           152 B          87.5 kB
└ ○ /workspace                           152 B          87.5 kB
+ First Load JS shared by all            87.3 kB
  ├ chunks/117-c2e8725fecde5126.js       31.7 kB
  ├ chunks/fd9d1056-307a36020502e7d7.js  53.6 kB
  └ other shared chunks (total)          1.95 kB


ƒ Middleware                             26.9 kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand


```

### STDERR

```text

```
