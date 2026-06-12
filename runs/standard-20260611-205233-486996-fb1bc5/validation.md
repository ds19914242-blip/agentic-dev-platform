# Validation Result

## Overall Result

failed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: failed

Timed Out: False

Exit Code: 2

### STDOUT

```text
lib/rss/collect.ts(20,9): error TS2304: Cannot find name 'SourceType'.

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

```

### STDERR

```text
Failed to compile.

./lib/rss/collect.ts:20:9
Type error: Cannot find name 'SourceType'.

[0m [90m 18 |[39m   id[33m:[39m string[33m;[39m[0m
[0m [90m 19 |[39m   name[33m:[39m string[33m;[39m[0m
[0m[31m[1m>[22m[39m[90m 20 |[39m   type[33m:[39m [33mSourceType[39m[33m;[39m[0m
[0m [90m    |[39m         [31m[1m^[22m[39m[0m
[0m [90m 21 |[39m   status[33m:[39m string[33m;[39m[0m
[0m [90m 22 |[39m   itemCount[33m:[39m number[33m;[39m[0m
[0m [90m 23 |[39m   error[33m?[39m[33m:[39m string[33m;[39m[0m
Next.js build worker exited with code: 1 and signal: null

```
