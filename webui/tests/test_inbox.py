#!/usr/bin/env python3
"""Unit tests for console.inbox — typed intake persistence (Phase 5b).

Hermetic: a temp dir stands in for the backlog. Run:

    python3 webui/tests/test_inbox.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import inbox  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def test_empty_and_path():
    with tempfile.TemporaryDirectory() as d:
        check("inbox_path is _inbox.json", inbox.inbox_path(d).name == "_inbox.json")
        check("load empty -> items []", inbox.load(d) == {"items": []})
        check("list empty -> items []", inbox.list_items(d, "")["items"] == [])


def test_add_and_list():
    with tempfile.TemporaryDirectory() as d:
        r = inbox.add(d, "prodA", "epic", "Build a thing")
        check("add returns ok+item", r.get("ok") and r["item"]["text"] == "Build a thing")
        check("add assigns id", bool(r["item"].get("id")))
        check("add sets status new", r["item"]["status"] == "new")
        check("add keeps valid type", r["item"]["type"] == "epic")
        items = inbox.list_items(d, "")["items"]
        check("list shows the item", len(items) == 1 and items[0]["text"] == "Build a thing")
        check("persisted as json", isinstance(json.loads(inbox.inbox_path(d).read_text()), dict))


def test_type_normalization_and_empty_text():
    with tempfile.TemporaryDirectory() as d:
        check("bad type -> task", inbox.add(d, "p", "weird", "x")["item"]["type"] == "task")
        check("bug type preserved", inbox.add(d, "p", "bug", "y")["item"]["type"] == "bug")
        check("task type preserved", inbox.add(d, "p", "task", "z")["item"]["type"] == "task")
        r = inbox.add(d, "p", "task", "   ")
        check("empty text rejected", r.get("ok") is False and "empty" in r.get("error", ""))


def test_product_filter():
    with tempfile.TemporaryDirectory() as d:
        inbox.add(d, "prodA", "task", "a1")
        inbox.add(d, "prodB", "task", "b1")
        check("filter by product", len(inbox.list_items(d, "prodA")["items"]) == 1)
        check("no filter shows all", len(inbox.list_items(d, "")["items"]) == 2)


def test_delete():
    with tempfile.TemporaryDirectory() as d:
        iid = inbox.add(d, "p", "task", "to delete")["item"]["id"]
        inbox.add(d, "p", "task", "to keep")
        r = inbox.delete(d, iid)
        check("delete removes one", r["removed"] == 1)
        left = inbox.list_items(d, "")["items"]
        check("only the other remains", len(left) == 1 and left[0]["text"] == "to keep")
        check("delete missing id removes 0", inbox.delete(d, "nope")["removed"] == 0)


def test_corrupt_file():
    with tempfile.TemporaryDirectory() as d:
        inbox.inbox_path(d).write_text("{ broken")
        check("corrupt file loads empty", inbox.load(d) == {"items": []})
        check("add recovers after corrupt", inbox.add(d, "p", "task", "ok")["ok"] is True)


def main():
    for t in (test_empty_and_path, test_add_and_list, test_type_normalization_and_empty_text,
              test_product_filter, test_delete, test_corrupt_file):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"inbox: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
