#!/usr/bin/env python3
"""Agentic Console — smoke / regression detector.

Boots webui/server.py on an alt port and checks that every key endpoint still
answers with sane JSON, and that the frontend and backend agree on version.
It does NOT exercise git/agent flows (those need the real product repo); it is a
"the wiring still works" guard for refactoring. Runs the same in the sandbox and
on the user's machine — on the machine it will also hit the real product.

Usage:  python3 webui/tests/test_smoke.py
Exit code 0 = all passed, 1 = at least one failure.
"""
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
ROOT = os.path.dirname(WEBUI)
SERVER = os.path.join(WEBUI, "server.py")
INDEX = os.path.join(WEBUI, "static", "index.html")

PASS, FAIL = [], []


def ok(name, detail=""):
    PASS.append(name)
    print("  \033[32mPASS\033[0m", name)


def bad(name, detail=""):
    FAIL.append((name, detail))
    print("  \033[31mFAIL\033[0m", name, ("— " + detail) if detail else "")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def get(base, path, **q):
    url = base + path + (("?" + urllib.parse.urlencode(q)) if q else "")
    with urllib.request.urlopen(url, timeout=10) as r:
        body = r.read().decode()
    return r.status, body


def get_json(base, path, **q):
    st, body = get(base, path, **q)
    return st, json.loads(body)


def file_version(path, pattern):
    m = re.search(pattern, open(path, encoding="utf-8").read())
    return m.group(1) if m else None


def main():
    # --- static checks (no server needed) -------------------------------
    print("static:")
    api_v = file_version(SERVER, r'API_VERSION\s*=\s*"([^"]+)"')
    fe_v = file_version(INDEX, r'FE_VERSION\s*=\s*"([^"]+)"')
    if api_v and fe_v and api_v == fe_v:
        ok(f"version sync ({api_v})")
    else:
        bad("version sync", f"server={api_v} frontend={fe_v}")

    # frontend balance: braces / parens / backticks inside <script>
    html = open(INDEX, encoding="utf-8").read()
    try:
        body = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]
        b = body.count("{") - body.count("}")
        p = body.count("(") - body.count(")")
        t = body.count("`") % 2
        if (b, p, t) == (0, 0, 0):
            ok("frontend braces/parens/backticks balanced")
        else:
            bad("frontend balance", f"{{}}={b} ()={p} ``={t}")
    except Exception as e:
        bad("frontend balance", str(e))

    # --- boot the server ------------------------------------------------
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    print(f"server: booting on {port} (cwd={ROOT})")
    proc = subprocess.Popen(
        [sys.executable, SERVER, "--port", str(port)],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        up = False
        for _ in range(40):
            try:
                st, _ = get(base, "/api/version")
                if st == 200:
                    up = True
                    break
            except Exception:
                time.sleep(0.25)
        if not up:
            bad("server boots", "no response on /api/version")
            out = proc.stdout.read().decode(errors="ignore") if proc.stdout else ""
            print(out[-2000:])
            return finish()
        ok("server boots")

        # version endpoint
        try:
            _, v = get_json(base, "/api/version")
            (ok if v.get("api_version") == api_v else bad)(
                "/api/version matches file",
                "" if v.get("api_version") == api_v else f"{v.get('api_version')} != {api_v}")
        except Exception as e:
            bad("/api/version", str(e))

        # state — discover a product to scope the rest
        product = ""
        try:
            _, state = get_json(base, "/api/state")
            for key in ("products", "api_version", "version"):
                pass
            if isinstance(state.get("products"), list):
                ok("/api/state shape")
                if state["products"]:
                    product = state["products"][0].get("name", "")
            else:
                bad("/api/state shape", "no products list")
        except Exception as e:
            bad("/api/state", str(e))

        # endpoints that must return valid JSON (200) regardless of product
        checks = [
            ("/api/inbox", {"product": product}, "items"),
            ("/api/epics/overview", {"product": product}, "epics"),
            ("/api/epics/archived", {"product": product}, "epics"),
        ]
        for path, q, key in checks:
            try:
                st, data = get_json(base, path, **q)
                if st == 200 and key in data:
                    ok(f"{path} -> has '{key}'")
                else:
                    bad(f"{path}", f"status={st} keys={list(data)[:6]}")
            except Exception as e:
                bad(path, str(e))

        # inbox round-trip: add -> list -> delete (uses a throwaway product tag)
        try:
            req = urllib.request.Request(
                base + "/api/inbox/add",
                data=json.dumps({"product": "__smoke__", "type": "bug",
                                 "text": "smoke probe"}).encode(),
                headers={"Content-Type": "application/json"})
            added = json.loads(urllib.request.urlopen(req, timeout=10).read())
            iid = added.get("item", {}).get("id")
            _, lst = get_json(base, "/api/inbox", product="__smoke__")
            present = any(i.get("id") == iid for i in lst.get("items", []))
            req2 = urllib.request.Request(
                base + "/api/inbox/delete",
                data=json.dumps({"id": iid}).encode(),
                headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req2, timeout=10).read()
            _, lst2 = get_json(base, "/api/inbox", product="__smoke__")
            gone = not any(i.get("id") == iid for i in lst2.get("items", []))
            (ok if (iid and present and gone) else bad)(
                "inbox add/list/delete round-trip",
                "" if (iid and present and gone) else f"add={bool(iid)} present={present} gone={gone}")
        except Exception as e:
            bad("inbox round-trip", str(e))

        # index served and carries the frontend
        try:
            st, page = get(base, "/")
            (ok if (st == 200 and "FE_VERSION" in page and "Object.assign" in page) else bad)(
                "/ serves frontend", "" if st == 200 else f"status={st}")
        except Exception as e:
            bad("/ serves frontend", str(e))

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    return finish()


def finish():
    print()
    print(f"smoke: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n, d in FAIL:
            print("  -", n, ("— " + d) if d else "")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
