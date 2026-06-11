# Validation Result

## Overall Result

failed

## typecheck

Required: True

Command: `npx tsc --noEmit`

Result: failed

Timed Out: False

Exit Code: 1

### STDOUT

```text

[41m                                                                               [0m
[41m[37m                This is not the tsc command you are looking for                [0m
[41m                                                                               [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages

```

### STDERR

```text

```

## build

Required: True

Command: `npm run build`

Result: failed

Timed Out: False

Exit Code: 127

### STDOUT

```text

> rss-agent-lab@1.0.0 build
> next build


```

### STDERR

```text
sh: next: command not found

```
