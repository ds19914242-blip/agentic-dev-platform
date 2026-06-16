#!/usr/bin/env python3
"""Tests for preview env seeding (ws-50).

The epic preview runs from a fresh git worktree, where gitignored env files (.env.local with
SESSION_SECRET + real creds) don't exist — so login used to 500 / use wrong creds. _seed_preview_env
copies the product repo's real env into the worktree, falling back to a synthetic .env.local only
if the product ships none. Hermetic: temp 'repo' + temp 'worktree'. Run:

    python3 webui/tests/test_preview.py
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
ROOT = os.path.dirname(WEBUI)
sys.path.insert(0, ROOT)
sys.path.insert(0, WEBUI)

import server  # noqa: E402  (main() is __main__-guarded)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def test_copies_real_env():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        (repo / ".env.local").write_text("SESSION_SECRET=real_secret_123\nAPP_PASSWORD=password123\n")
        (repo / ".env").write_text("DATABASE_URL=postgres://x\n")
        copied = server._seed_preview_env(str(repo), str(wt))
        check("reports copied env files", set(copied) == {".env", ".env.local"})
        check("worktree .env.local has the REAL secret",
              "real_secret_123" in (wt / ".env.local").read_text())
        check("worktree .env copied too", (wt / ".env").exists())


def test_does_not_overwrite_existing():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        (repo / ".env.local").write_text("SESSION_SECRET=from_repo\n")
        (wt / ".env.local").write_text("SESSION_SECRET=already_here\n")
        copied = server._seed_preview_env(str(repo), str(wt))
        check("does not clobber an existing worktree env", ".env.local" not in copied)
        check("existing worktree env preserved",
              "already_here" in (wt / ".env.local").read_text())


def test_synthetic_fallback_when_no_repo_env():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        wt = Path(tmp) / "wt"
        repo.mkdir()
        wt.mkdir()
        copied = server._seed_preview_env(str(repo), str(wt))
        check("nothing copied when repo has no env", copied == [])
        check("synthetic .env.local written as fallback", (wt / ".env.local").exists())
        body = (wt / ".env.local").read_text()
        check("synthetic fallback has a SESSION_SECRET", "SESSION_SECRET=" in body)


def test_smoke_verdict():
    from console.serializers import smoke_verdict as v
    check("200 -> ok", v(200) == "ok")
    check("204 -> ok", v(204) == "ok")
    check("404 -> missing", v(404) == "missing")
    check("500 -> error", v(500) == "error")
    check("503 -> error", v(503) == "error")
    check("307 -> auth (redirected to login)", v(307) == "auth")
    check("403 -> auth", v(403) == "auth")
    check("0/unknown -> other", v(0) == "other")


def test_parse_env():
    body = '# comment\nAPP_USERNAME=admin\nAPP_PASSWORD="p@ss word"\nSESSION_SECRET=abc\n\nBAD LINE\n'
    env = server._parse_env(body)
    check("parses key=value", env.get("APP_USERNAME") == "admin")
    check("strips quotes", env.get("APP_PASSWORD") == "p@ss word")
    check("skips comments and junk", "BAD LINE" not in env and len(env) == 3)


def _stub_server(login_status=200, set_cookie=True):
    """A throwaway HTTP app: login + a few routes with distinct statuses."""
    import http.server
    import threading

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            ln = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(ln)
            self.send_response(login_status)
            if login_status < 300 and set_cookie:
                self.send_header("Set-Cookie", "SESSION=abc123; Path=/")
            self.end_headers()
            self.wfile.write(b"{}")

        def do_GET(self):
            codes = {"/sources": 200, "/": 200, "/saved": 404, "/boom": 500}
            code = codes.get(self.path, 404)
            self.send_response(code)
            self.end_headers()
            self.wfile.write(b"ok" if code == 200 else b"x")

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def test_run_smoke_against_stub():
    srv, base = _stub_server()
    try:
        res = server._run_smoke(base, "/api/auth/login", {"username": "u", "password": "p"},
                                ["/sources", "/saved", "/boom"], timeout=5)
        check("login succeeds when cookie is set", res["login"] is True)
        by = {r["route"]: r["verdict"] for r in res["results"]}
        check("valid route -> ok", by.get("/sources") == "ok")
        check("missing route -> missing (the /saved defect, live)", by.get("/saved") == "missing")
        check("crashing route -> error", by.get("/boom") == "error")
    finally:
        srv.shutdown()


def test_run_smoke_login_fails():
    srv, base = _stub_server(login_status=401, set_cookie=False)
    try:
        res = server._run_smoke(base, "/api/auth/login", {"username": "u", "password": "p"},
                                ["/sources"], timeout=5)
        check("login failure reported", res["login"] is False)
        check("no route probes when login fails", res["results"] == [])
    finally:
        srv.shutdown()


def main():
    for t in (test_copies_real_env, test_does_not_overwrite_existing,
              test_synthetic_fallback_when_no_repo_env,
              test_smoke_verdict, test_parse_env,
              test_run_smoke_against_stub, test_run_smoke_login_fails):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"preview: {len(PASS)} passed, {len(FAIL)} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
