#!/usr/bin/env python3
"""Contract tests for the platform's route verification (Phase: console Verify stage).

The console's new Verify stage calls orchestrator.route_verification.verify_routes
against a worktree of the assembled epic branch. These tests pin the contract that
wiring relies on (input dirs, how routes are detected, result shape), so a change in
the platform's verifier surfaces here instead of silently breaking the console.

Hermetic: temp epic dir (spec) + temp repo (Next.js-ish app tree). Run:

    python3 webui/tests/test_verify.py
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
ROOT = os.path.dirname(WEBUI)
sys.path.insert(0, ROOT)   # platform root, for orchestrator
sys.path.insert(0, WEBUI)

from orchestrator.route_verification import verify_routes  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def _mk_repo(tmp, page_routes=(), api_routes=()):
    """Create a minimal Next.js app/ tree with the given page/api routes present."""
    repo = Path(tmp) / "repo"
    for r in page_routes:
        d = repo / "app" / r.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        (d / "page.tsx").write_text("export default function P(){return null}")
    for r in api_routes:
        seg = r.strip("/")
        seg = seg[len("api/"):] if seg.startswith("api/") else seg
        d = repo / "app" / "api" / seg
        d.mkdir(parents=True, exist_ok=True)
        (d / "route.ts").write_text("export function GET(){}")
    repo.mkdir(parents=True, exist_ok=True)
    return repo


def _mk_epic(tmp, spec_text):
    ed = Path(tmp) / "backlog" / "epicV"
    ed.mkdir(parents=True, exist_ok=True)
    (ed / "feature-spec.md").write_text(spec_text)
    return ed


def test_missing_route_detected():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _mk_repo(tmp, page_routes=["/settings"])  # /billing intentionally absent
        ed = _mk_epic(tmp, "The app exposes `/settings` and `/billing` pages.\n")
        res = verify_routes(ed, str(repo))
        check("result shape has expected keys",
              all(k in res for k in ("result", "routes", "api_routes", "missing")))
        routes = {r["route"]: r["exists"] for r in res["routes"]}
        check("present page route detected as existing", routes.get("/settings") is True)
        check("missing page route detected as absent", routes.get("/billing") is False)
        check("overall result failed when something missing", res["result"] == "failed")
        miss = {m["route"] for m in res["missing"]}
        check("missing list names /billing", "/billing" in miss and "/settings" not in miss)


def test_all_present_passes():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _mk_repo(tmp, page_routes=["/settings", "/dashboard"], api_routes=["/api/users"])
        ed = _mk_epic(tmp, "Pages `/settings` and `/dashboard`; API `/api/users`.\n")
        res = verify_routes(ed, str(repo))
        check("all present -> passed", res["result"] == "passed", str(res["missing"]))
        check("api route detected as existing",
              any(a["route"] == "/api/users" and a["exists"] for a in res["api_routes"]))
        check("no missing", res["missing"] == [])


def test_no_route_literals():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _mk_repo(tmp)
        ed = _mk_epic(tmp, "This feature improves performance and adds caching. No routes.\n")
        res = verify_routes(ed, str(repo))
        check("no route mentions -> passed (nothing missing)", res["result"] == "passed")
        check("empty page route list", res["routes"] == [])


def test_asset_and_speculative_filtered():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _mk_repo(tmp)  # nothing present
        # /logo.png is an asset; the e.g. line makes /alpha speculative (example, not a promise)
        ed = _mk_epic(tmp, "Show `/logo.png` somewhere. A page e.g. `/alpha` or `/beta`.\n")
        res = verify_routes(ed, str(repo))
        listed = {r["route"] for r in res["routes"]}
        check("asset route /logo.png excluded", "/logo.png" not in listed)
        check("speculative example route excluded from required set",
              "/alpha" not in {m["route"] for m in res["missing"]})


def test_file_to_route():
    from console.serializers import file_to_route as f
    check("root page", f("app/page.tsx") == ("/", "page"))
    check("simple page", f("app/notes/page.tsx") == ("/notes", "page"))
    check("dynamic page kept verbatim", f("app/notes/[id]/page.tsx") == ("/notes/[id]", "page"))
    check("catch-all kept", f("app/docs/[...slug]/page.tsx") == ("/docs/[...slug]", "page"))
    check("route group stripped", f("app/(marketing)/about/page.tsx") == ("/about", "page"))
    check("src/app prefix", f("src/app/dashboard/page.tsx") == ("/dashboard", "page"))
    check("api route", f("app/api/notes/route.ts") == ("/api/notes", "api"))
    check("dynamic api route", f("app/api/notes/[id]/route.ts") == ("/api/notes/[id]", "api"))
    check("page.js variant", f("app/x/page.js") == ("/x", "page"))
    check("layout is not a route", f("app/notes/layout.tsx") is None)
    check("non-app file is not a route", f("components/Card.tsx") is None)


def test_nav_hrefs():
    from console.serializers import nav_hrefs as nh
    src = '''
      const LINKS = [
        { href: "/dashboard", label: "Dash" },
        { href: "/saved", label: "Сохранённые" },
        { href: '/admin/users', label: "Users" },
      ];
      <Link href="/dashboard">brand</Link>
      <a href="https://example.com">ext</a>
      <a href="//cdn.example.com/x">proto</a>
      <a href="mailto:x@y.z">mail</a>
      <a href="#top">anchor</a>
      <Link href={`/run/${id}`}>dynamic</Link>
      <Link href="/sources?tab=all#x">query</Link>
    '''
    got = nh(src)
    check("extracts object-config hrefs", "/dashboard" in got and "/saved" in got)
    check("extracts single-quoted href", "/admin/users" in got)
    check("dedupes brand+link /dashboard", got.count("/dashboard") == 1)
    check("skips external https", "https://example.com" not in " ".join(got) and not any("example.com" in g for g in got))
    check("skips protocol-relative //", not any(g.startswith("//") for g in got))
    check("skips mailto/anchor", not any("mailto" in g or g.startswith("#") for g in got))
    check("skips template-literal href", not any("run" in g for g in got))
    check("strips query/hash", "/sources" in got and "/sources?tab=all" not in got)


def test_route_set_has():
    from console.serializers import route_set_has as has
    routes = {"/", "/dashboard", "/admin/users", "/run/[id]", "/docs/[...slug]"}
    check("exact static match", has("/dashboard", routes))
    check("nested static match", has("/admin/users", routes))
    check("root match", has("/", routes))
    check("dynamic [id] wildcard match", has("/run/123", routes))
    check("catch-all match (1 seg)", has("/docs/intro", routes))
    check("catch-all match (deep)", has("/docs/a/b/c", routes))
    check("missing route -> no match (the /saved case)", not has("/saved", routes))
    check("static /run has no index page -> no match", not has("/run", routes))


def test_nav_orphans_tree():
    """End-to-end of the helper logic on a real tree: NavBar links to /dashboard (exists)
    and /saved (missing) -> exactly one orphan, /saved (the caught defect)."""
    from console.serializers import nav_hrefs, file_to_route, route_set_has
    with tempfile.TemporaryDirectory() as tmp:
        wt = Path(tmp)
        (wt / "components").mkdir()
        (wt / "components" / "NavBar.tsx").write_text(
            'const LINKS=[{href:"/dashboard",label:"D"},{href:"/saved",label:"S"}];'
        )
        for r in ["dashboard", "sources"]:
            d = wt / "app" / r
            d.mkdir(parents=True)
            (d / "page.tsx").write_text("export default function P(){}")
        # replicate _nav_orphans' core
        hrefs = nav_hrefs((wt / "components" / "NavBar.tsx").read_text())
        routes = set()
        for pf in (wt / "app").rglob("page.*"):
            m = file_to_route(str(pf.relative_to(wt)))
            if m and m[1] == "page":
                routes.add(m[0])
        orphans = [h for h in hrefs if not route_set_has(h, routes)]
        check("dashboard link resolves (not orphan)", "/dashboard" not in orphans)
        check("saved link flagged as orphan", orphans == ["/saved"])


def test_criterion_routes():
    from console.serializers import criterion_routes as cr
    check("plain route", cr("На /saved виден список") == ["/saved"])
    check("api route in backticks", cr("GET `/api/saved` возвращает список") == ["/api/saved"])
    check("dynamic route", cr("/saved/[id] открывает один материал") == ["/saved/[id]"])
    check("multiple routes deduped", cr("`/api/saved` POST и `/api/saved` GET") == ["/api/saved"])
    check("two distinct routes", set(cr("страницы /saved и /saved/new")) == {"/saved", "/saved/new"})
    check("no route -> empty", cr("empty-state оформлено, заметка редактируется") == [])
    check("date is not a route", cr("релиз 12/06/2026 готов") == [])
    check("trailing punct stripped", cr("открой /saved.") == ["/saved"])
    # ws-52 regressions: file paths must NOT be read as routes (the Status-epic false-✗ bug)
    check("file path /…/route.ts is not a route", cr("A route exists at `app/api/status/route.ts`") == [])
    check("lib/version.ts does not yield /version",
          cr("displays the version via `lib/version.ts`") == [])
    check("quoted page file dropped", cr("page at `app/status/page.tsx`") == [])
    check("real route survives next to a file mention",
          cr("`/status` page reads from `lib/version.ts`") == ["/status"])


def test_criterion_state():
    from console.serializers import criterion_state as cs
    branch = ["/saved", "/saved/[id]", "/api/saved", "/api/saved/[id]", "/sources"]
    st, _ = cs("На /saved виден список", branch)
    check("present route -> confirmed", st == "confirmed")
    st, _ = cs("/saved/[id] открывает материал", branch)
    check("present dynamic -> confirmed", st == "confirmed")
    st, _ = cs("empty-state оформлено", branch)
    check("no route -> review", st == "review")
    st, why = cs("GET `/api/missing` отдаёт данные", branch)
    check("absent route -> not_met", st == "not_met")
    check("not_met explains which route", "/api/missing" in why)
    # the 101806 case: nothing built -> all route criteria not_met
    st, why = cs("На /saved виден список", [], nav_orphans=["/saved"])
    check("empty branch -> route criterion not_met", st == "not_met")
    check("nav-orphan reinforces reason", "nav" in why.lower())


def test_routes_added_from_diff():
    """The high-recall view: enumerate route files the epic branch added vs base.
    Builds a real throwaway repo, branches, adds page/api files, and checks the mapping —
    crucially that dynamic [id] routes (invisible to the spec heuristic) ARE captured here."""
    import subprocess

    def run(repo, *a):
        return subprocess.run(["git", "-C", str(repo)] + list(a), capture_output=True, text=True)

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        run(repo, "init", "-q")
        run(repo, "config", "user.email", "t@t.t")
        run(repo, "config", "user.name", "t")
        run(repo, "checkout", "-q", "-b", "main")
        (repo / "app").mkdir()
        (repo / "app" / "page.tsx").write_text("export default function H(){}")
        run(repo, "add", "-A")
        run(repo, "commit", "-qm", "base")

        run(repo, "checkout", "-q", "-b", "agentic/epic-x")
        for rel in ["app/notes/page.tsx", "app/notes/new/page.tsx",
                    "app/notes/[id]/page.tsx", "app/api/notes/route.ts",
                    "app/api/notes/[id]/route.ts", "app/notes/layout.tsx"]:
            fp = repo / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("x")
        run(repo, "add", "-A")
        run(repo, "commit", "-qm", "notes feature")

        # mirror what the server helper does (diff base...HEAD -> file_to_route)
        from console.serializers import file_to_route
        diff = run(repo, "diff", "--name-status", "main...HEAD").stdout
        routes = []
        for line in diff.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            m = file_to_route(parts[-1].strip())
            if m:
                routes.append(m[0])
        check("captures static added routes", "/notes" in routes and "/notes/new" in routes)
        check("captures DYNAMIC route (spec heuristic could not)", "/notes/[id]" in routes)
        check("captures api routes incl dynamic",
              "/api/notes" in routes and "/api/notes/[id]" in routes)
        check("ignores layout.tsx", all(r != "/notes/layout" for r in routes))
        check("base root page not counted as added", "/" not in routes)


def main():
    for t in (test_missing_route_detected, test_all_present_passes,
              test_no_route_literals, test_asset_and_speculative_filtered,
              test_file_to_route, test_routes_added_from_diff,
              test_nav_hrefs, test_route_set_has, test_nav_orphans_tree,
              test_criterion_routes, test_criterion_state):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"verify: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
