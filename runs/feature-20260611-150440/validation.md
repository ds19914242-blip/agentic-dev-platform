# Validation Result

## Overall Result

failed

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

Result: failed

Timed Out: False

Exit Code: 1

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build

  ▲ Next.js 14.2.35
  - Environments: .env

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

```

### STDERR

```text

> Build error occurred
Error: ENOENT: no such file or directory, rename '/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/export/500.html' -> '/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/server/pages/500.html'
    at async Object.rename (node:internal/fs/promises:785:10)
    at async /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/build/index.js:1873:33
    at async Span.traceAsyncFn (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/trace/trace.js:154:20)
    at async /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/build/index.js:1924:25
    at async Span.traceAsyncFn (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/trace/trace.js:154:20)
    at async /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/build/index.js:1546:17
    at async Span.traceAsyncFn (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/trace/trace.js:154:20)
    at async build (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/build/index.js:368:9) {
  errno: -2,
  code: 'ENOENT',
  syscall: 'rename',
  path: '/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/export/500.html',
  dest: '/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/server/pages/500.html'
}

```
