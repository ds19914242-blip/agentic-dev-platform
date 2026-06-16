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


_ROUTE_PAGE_FILES = ("page.tsx", "page.ts", "page.jsx", "page.js")
_ROUTE_API_FILES = ("route.ts", "route.js", "route.tsx", "route.jsx")


def file_to_route(path):
    """Map a Next.js app-router file path to (url_route, kind) or None if not a route file.
    Pure. Handles app/ and src/app/, page vs route (api), dynamic [id]/[...slug] segments
    (kept verbatim), and route groups (parens) which are stripped from the URL.

        app/page.tsx                -> ('/', 'page')
        app/notes/page.tsx          -> ('/notes', 'page')
        app/notes/[id]/page.tsx     -> ('/notes/[id]', 'page')
        app/(marketing)/about/...   -> ('/about', 'page')
        src/app/api/notes/route.ts  -> ('/api/notes', 'api')
    """
    p = (path or "").strip()
    for pre in ("src/app/", "app/"):
        if p.startswith(pre):
            p = p[len(pre):]
            break
    else:
        return None
    fname = p.rsplit("/", 1)[-1]
    if fname in _ROUTE_PAGE_FILES:
        kind = "page"
    elif fname in _ROUTE_API_FILES:
        kind = "api"
    else:
        return None
    seg = p[: len(p) - len(fname)].rstrip("/")
    parts = [s for s in seg.split("/") if s and not (s.startswith("(") and s.endswith(")"))]
    route = "/" + "/".join(parts)
    return route, kind


_NAV_HREF_RE = re.compile(r"""href\s*[:=]\s*\{?\s*(["'])(/[^"']*)\1""")


def nav_hrefs(text):
    """Extract internal nav hrefs from a nav component's source (NavBar.tsx etc.).
    Pure. Handles object config (href: "/x") and JSX (<Link href="/x">, href={"/x"}),
    single or double quotes. Skips:
      - external/protocol-relative (//cdn, http…, mailto:, tel:, #anchor — don't start with one '/')
      - template-literal hrefs (backtick) — can't be resolved statically
    Strips query/hash. Returns deduped list preserving order."""
    out, seen = [], set()
    for m in _NAV_HREF_RE.finditer(text or ""):
        h = m.group(2)
        h = h.split("#", 1)[0].split("?", 1)[0]
        if not h or h.startswith("//"):
            continue
        if h != "/":
            h = h.rstrip("/")
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def _route_matches(href, route):
    """Does a concrete nav href match a (possibly dynamic) app-router route?
    [param] segments are wildcards; a trailing [...catch-all] absorbs >=1 segment.
    Pure, segment-wise."""
    h = [s for s in href.split("/") if s]
    r = [s for s in route.split("/") if s]
    catch = bool(r) and r[-1].startswith("[...") and r[-1].endswith("]")
    if catch:
        prefix = r[:-1]
        if len(h) < len(r):  # catch-all needs at least one segment of its own
            return False
        for hs, rs in zip(h[: len(prefix)], prefix):
            if rs.startswith("[") and rs.endswith("]"):
                continue
            if hs != rs:
                return False
        return True
    if len(h) != len(r):
        return False
    for hs, rs in zip(h, r):
        if rs.startswith("[") and rs.endswith("]"):
            continue
        if hs != rs:
            return False
    return True


def route_set_has(href, routes):
    """True if href resolves to any route in the set (exact or via dynamic wildcards). Pure."""
    return any(_route_matches(href, r) for r in routes)


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
