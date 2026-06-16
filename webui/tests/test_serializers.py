#!/usr/bin/env python3
"""Unit tests for console.serializers — pure parse/format (Phase 5c).

Fully hermetic: no files, no globals. Run:

    python3 webui/tests/test_serializers.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEBUI = os.path.dirname(HERE)
sys.path.insert(0, WEBUI)

from console import serializers as ser  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  \033[32mPASS\033[0m " if cond else "  \033[31mFAIL\033[0m ") + name +
          (("" if cond else (" — " + detail)) if detail else ""))


def test_section():
    text = "## Request\nBuild a thing\nmore\n\n## Other\nnope\n"
    check("section extracts body", ser.section(text, "Request") == "Build a thing\nmore")
    check("section stops at next ##", "nope" not in ser.section(text, "Request"))
    check("section missing -> ''", ser.section(text, "Nonexistent") == "")
    check("section escapes heading regex", ser.section("## A.B\nx\n", "A.B") == "x")


def test_parse_task_basic():
    md = ("### Task 3: Wire up the navbar\n"
          "Status: implemented\n"
          "Type: feature\n"
          "PR: 42\n"
          "Run: agentic/task-x\n"
          "## Depends On\n"
          "- task-001\n"
          "- task-002\n"
          "## Notes\n"
          "irrelevant\n")
    out = ser.parse_task(md, "task-003.md")
    check("parse title from ###", out["title"] == "Task 3: Wire up the navbar")
    check("parse status", out["status"] == "implemented")
    check("parse pr", out["pr"] == "42")
    check("parse run", out["run"] == "agentic/task-x")
    check("parse deps", out["depends_on"] == ["task-001", "task-002"])
    check("file is the name", out["file"] == "task-003.md")
    check("deps stop at next ##", "irrelevant" not in out["depends_on"])


def test_parse_task_edges():
    out = ser.parse_task("no fields here\n", "task-009.md")
    check("title defaults to filename", out["title"] == "task-009.md")
    check("empty status", out["status"] == "")
    check("no deps", out["depends_on"] == [])
    none = ser.parse_task("## Depends On\n_None_\n", "t.md")
    check("_None_ yields no deps", none["depends_on"] == [])
    # '**Status**:' style lines are ignored (line starts with **)
    bold = ser.parse_task("**Status**: x\nStatus: real\n", "t.md")
    check("bold pseudo-field ignored, real one kept", bold["status"] == "real")


def test_parse_tsc_errors():
    txt = ("src/a.ts(12,4): error TS2304: Cannot find name 'Foo'.\n"
           "src/a.ts(20,1): error TS2339: Property 'bar' does not exist.\n"
           "noise line that should be ignored\n"
           "src/b.ts(3,3): error TS2307: Cannot find module 'x'.\n")
    files, symbols = ser.parse_tsc_errors(txt)
    check("groups errors by file", len(files["src/a.ts"]) == 2)
    check("captures second file", "src/b.ts" in files)
    check("ignores non-error lines", all("noise" not in e for errs in files.values() for e in errs))
    check("counts undefined symbol Foo", symbols.get("Foo") == 1)
    check("symbol from TS2339 captured", "bar" in symbols)
    check("empty input -> empty", ser.parse_tsc_errors("") == ({}, {}))


def test_eff_status():
    DONE = {"done", "merged"}
    check("accepted run wins", ser.eff_status("todo", "accepted", DONE) == "accepted")
    check("done status -> done", ser.eff_status("done", None, DONE) == "done")
    check("running", ser.eff_status("todo", "running", DONE) == "running")
    check("failed", ser.eff_status("todo", "failed", DONE) == "failed")
    check("interrupted", ser.eff_status("todo", "interrupted", DONE) == "interrupted")
    check("implemented", ser.eff_status("todo", "implemented", DONE) == "implemented")
    check("no_changes -> implemented", ser.eff_status("todo", "no_changes", DONE) == "implemented")
    check("fallback to task status", ser.eff_status("in_review", None, DONE) == "in_review")
    check("fallback to todo when empty", ser.eff_status("", None, DONE) == "todo")
    check("accepted precedence over running", ser.eff_status("x", "accepted", DONE) == "accepted")


def main():
    for t in (test_section, test_parse_task_basic, test_parse_task_edges,
              test_parse_tsc_errors, test_eff_status):
        print(t.__name__ + ":")
        try:
            t()
        except Exception as exc:
            FAIL.append(t.__name__)
            print("  \033[31mERROR\033[0m", t.__name__, "—", exc)
    print()
    print(f"serializers: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        for n in FAIL:
            print("  -", n)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
