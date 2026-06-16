"""console.serializers — pure parsing/formatting for the Agentic Console.

Extracted verbatim from server.py (Phase 5c). Everything here is a pure function
of its inputs — no file I/O, no globals, no side effects — which makes the fiddly
text parsing (markdown sections, task files, tsc errors) and the effective-status
mapping directly unit-testable. server.py keeps thin same-named wrappers/aliases.

Behaviour is byte-for-byte identical to the originals.
"""
import re


def section(text, heading):
    """Return the body of a `## <heading>` markdown section, or '' if absent."""
    m = re.search(rf"##\s*{re.escape(heading)}\s*\n+(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_task(text, name):
    """Parse a task markdown body (plus its filename) into a structured dict.
    Pure version of the old _parse_task_file, which read the file then called this."""
    fields, deps, title, in_deps = {}, [], name, False
    for line in text.splitlines():
        ls = line.strip()
        if ls.startswith("### ") and title == name:
            title = ls.lstrip("# ").strip()
        if ":" in line and not line.startswith("#") and not line.startswith("**"):
            k, _, v = line.partition(":")
            k = k.strip().lower()
            if k in {"status", "type", "pipeline", "risk", "pr", "run"}:
                fields.setdefault(k, v.strip())
        if ls.lower().startswith("## depends"):
            in_deps = True
            continue
        if in_deps:
            if ls.startswith("## "):
                in_deps = False
            elif ls and ls != "_None_" and not ls.startswith("_"):
                deps.append(ls.lstrip("- ").strip())
    return {"file": name, "title": title, "status": fields.get("status", ""),
            "pr": fields.get("pr", ""), "run": fields.get("run", ""), "depends_on": deps}


def parse_tsc_errors(text):
    """Parse `file(line,col): error TSxxxx: msg` lines into {file:[errs]} and
    {symbol:count} for symbols that are undefined/removed but still referenced."""
    files, symbols = {}, {}
    for line in (text or "").splitlines():
        m = re.match(r"^\s*(\S.*?)\((\d+),(\d+)\):\s*error\s+(TS\d+):\s*(.*)$", line)
        if not m:
            continue
        f, ln, _col, code, msg = m.groups()
        files.setdefault(f, []).append(f"L{ln} {code}: {msg}")
        sm = re.search(r"'([^']+)'", msg)
        if sm and code in ("TS2304", "TS2305", "TS2307", "TS2552", "TS2614", "TS2724", "TS2339"):
            symbols[sm.group(1)] = symbols.get(sm.group(1), 0) + 1
    return files, symbols


def eff_status(task_status, rstate, done_statuses):
    """Collapse a task's declared status + its run-state into the single 'effective'
    status the UI shows. Pure mapping; done_statuses is injected (server constant)."""
    if task_status in done_statuses or rstate == "accepted":
        return "accepted" if rstate == "accepted" else "done"
    if rstate == "running":
        return "running"
    if rstate == "failed":
        return "failed"
    if rstate == "interrupted":
        return "interrupted"
    if rstate in ("implemented", "no_changes"):
        return "implemented"
    return task_status or "todo"
