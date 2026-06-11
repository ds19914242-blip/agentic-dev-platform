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
Could not find files for /_error in .next/build-manifest.json
Could not find files for /_error in .next/build-manifest.json
Could not find files for /_error in .next/build-manifest.json
Could not find files for /_error in .next/build-manifest.json
TypeError: Cannot read properties of undefined (reading 'call')
    at Object.t [as require] (/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/server/webpack-runtime.js:1:128)
    at require (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:17:18811)
    at s (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:88330)
    at /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:98875
    at /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:98962
    at t (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:99165) {
  digest: '4061325451'
}
TypeError: Cannot read properties of undefined (reading 'call')
    at Object.t [as require] (/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/server/webpack-runtime.js:1:128)
    at require (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:17:18811)
    at A (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:94398)
    at /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:96726
    at B._fromJSON (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:97164)
    at JSON.parse (<anonymous>)
    at I (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:94119)
    at t (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:100640)

Error occurred prerendering page "/login". Read more: https://nextjs.org/docs/messages/prerender-error

TypeError: Cannot read properties of undefined (reading 'call')
    at Object.t [as require] (/Users/danilsmetanev/Projects/rss-agent-lab_2/.next/server/webpack-runtime.js:1:128)
    at require (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:17:18811)
    at A (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:94398)
    at /Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:96726
    at B._fromJSON (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:97164)
    at JSON.parse (<anonymous>)
    at I (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:94119)
    at t (/Users/danilsmetanev/Projects/rss-agent-lab_2/node_modules/next/dist/compiled/next-server/app-page.runtime.prod.js:12:100640)

> Export encountered errors on following paths:
	/login/page: /login

```
