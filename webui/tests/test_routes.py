#!/usr/bin/env python3
"""Tests for the GET route table (Phase 4a).

Guards the dispatch refactor: the registry must stay complete (no endpoint lost),
duplicate-free, and every handler callable. A golden set of expected GET paths is
pinned here so a dropped or renamed route fails loudly. Run:

    python3 webui/tests/test_routes.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

import server  # noqa: E402  (imports the real module; main() is __main__-guarded)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


# The complete set of table-dispatched GET endpoints. The four special-cased paths
# ("/", "/index.html", "/static/*", "/api/job/stream") are handled in do_GET itself
# and are intentionally NOT in the table.
EXPECTED_GET = {
    "/api/state", "/api/inbox", "/api/epics", "/api/epics/overview", "/api/epics/archived",
    "/api/overview", "/api/backlog", "/api/task", "/api/task/diff", "/api/epic/build-status",
    "/api/epic/stage", "/api/epic/criteria", "/api/epic/fix-diff", "/api/epic/preview-log", "/api/preview/active",
    "/api/jobs/active", "/api/epic", "/api/runs", "/api/version", "/api/job",
    "/api/repo/tree", "/api/repo/file", "/api/repo/structure", "/api/repo/operational",
    "/api/repo/history", "/api/repo/baseline", "/api/repo/changes", "/api/repo/diff",
    "/api/git", "/api/analysis", "/api/file",
}

SPECIAL_GET = {"/", "/index.html", "/api/job/stream"}  # plus the /static/ prefix

# The complete set of POST endpoints (all table-dispatched; none stream).
EXPECTED_POST = {
    "/api/decompose", "/api/quick-task", "/api/inbox/add", "/api/inbox/delete",
    "/api/connect-repo", "/api/analyze", "/api/baseline", "/api/approve-product",
    "/api/approve-spec", "/api/epic/build", "/api/epic/preview-start", "/api/epic/preview-stop",
    "/api/epic/preview-mark", "/api/epic/push", "/api/epic/rollback", "/api/epic/fix-build",
    "/api/epic/validate", "/api/epic/verify", "/api/epic/reset-runs", "/api/task/reset", "/api/task/accept",
    "/api/task/run", "/api/epic/archive", "/api/epic/restore", "/api/epic/delete",
    "/api/commit-epic",
}


def test_registry_shape():
    for name, routes, expected in (("GET", server.GET_ROUTES, EXPECTED_GET),
                                   ("POST", server.POST_ROUTES, EXPECTED_POST)):
        check(f"{name}_ROUTES is a non-empty dict", isinstance(routes, dict) and len(routes) > 0)
        check(f"{name}: every handler is callable", all(callable(h) for h in routes.values()))
        check(f"{name}: no route count drift", len(routes) == len(expected),
              f"have {len(routes)}, expected {len(expected)}")


def test_golden_paths():
    have = set(server.GET_ROUTES)
    missing = EXPECTED_GET - have
    extra = have - EXPECTED_GET
    check("GET: no endpoint lost", not missing, "missing: " + ", ".join(sorted(missing)))
    check("GET: no unexpected endpoint", not extra, "extra: " + ", ".join(sorted(extra)))
    have_p = set(server.POST_ROUTES)
    miss_p = EXPECTED_POST - have_p
    extra_p = have_p - EXPECTED_POST
    check("POST: no endpoint lost", not miss_p, "missing: " + ", ".join(sorted(miss_p)))
    check("POST: no unexpected endpoint", not extra_p, "extra: " + ", ".join(sorted(extra_p)))


def test_special_paths_not_in_table():
    # the special-cased paths must NOT collide with table entries
    overlap = SPECIAL_GET & set(server.GET_ROUTES)
    check("special paths handled outside the table", not overlap,
          "overlap: " + ", ".join(sorted(overlap)))


def test_qp_helper():
    qp = server._qp
    check("_qp returns first value", qp({"product": ["a", "b"]}, "product") == "a")
    check("_qp default on missing", qp({}, "product") == "")
    check("_qp custom default", qp({}, "x", "z") == "z")


def test_handler_return_convention():
    # a pure handler that needs no server state: /api/version
    out = server.GET_ROUTES["/api/version"]({})
    check("/api/version handler returns body dict", out == {"api_version": server.API_VERSION},
          str(out))
    # a conditional-404 handler returns a (status, body) tuple when not found
    job_out = server.GET_ROUTES["/api/job"]({"id": ["nope"]})
    check("/api/job returns (404, body) when missing",
          isinstance(job_out, tuple) and job_out[0] == 404, str(job_out))


def test_post_validation_convention():
    # missing required fields -> (400, body), without side effects or server state
    d = server.POST_ROUTES["/api/decompose"]({})
    check("/api/decompose -> (400, ...) when empty",
          isinstance(d, tuple) and d[0] == 400, str(d))
    a = server.POST_ROUTES["/api/analyze"]({})
    check("/api/analyze -> (400, ...) without product",
          isinstance(a, tuple) and a[0] == 400, str(a))
    b = server.POST_ROUTES["/api/epic/build"]({"epic_id": "../bad"})
    check("/api/epic/build -> (400, ...) on invalid epic_id",
          isinstance(b, tuple) and b[0] == 400, str(b))
    t = server.POST_ROUTES["/api/task/accept"]({"epic_id": "x"})
    check("/api/task/accept -> (400, ...) without task_file",
          isinstance(t, tuple) and t[0] == 400, str(t))


def test_pp_helper():
    pp = server._pp
    check("_pp strips", pp({"epic_id": "  e1 "}, "epic_id") == "e1")
    check("_pp empty on missing", pp({}, "epic_id") == "")
    check("_pp handles None value", pp({"epic_id": None}, "epic_id") == "")


def main():
    for t in (test_registry_shape, test_golden_paths, test_special_paths_not_in_table,
              test_qp_helper, test_handler_return_convention,
              test_post_validation_convention, test_pp_helper):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"routes: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
