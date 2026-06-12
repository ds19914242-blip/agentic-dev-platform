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
app/sources/page.tsx(264,14): error TS1005: ';' expected.

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

```

### STDERR

```text
Failed to compile.

./app/sources/page.tsx
Error: 
  [31mx[0m Unexpected token `div`. Expected jsx identifier
     ,-[[36;1;4m/Users/danilsmetanev/Projects/rss-agent-lab_2/app/sources/page.tsx[0m:156:1]
 [2m156[0m |   }
 [2m157[0m | 
 [2m158[0m |   return (
 [2m159[0m |     <div className="animate-rise grid gap-6 py-4 lg:grid-cols-3">
     : [31;1m     ^^^[0m
 [2m160[0m |       {/* List */}
 [2m161[0m |       <div className="lg:col-span-2">
 [2m162[0m |         <div className="mb-4 flex items-center justify-between">
     `----

Caused by:
    Syntax Error

Import trace for requested module:
./app/sources/page.tsx


> Build failed because of webpack errors

```
