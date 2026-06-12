from __future__ import annotations

import ast
from pathlib import Path


LOCAL_MODULES = {
    "planner",
    "run_backlog_task",
    "run_fast_task",
    "run_standard_task",
    "run_autonomous_feature",
    "decompose_feature",
    "approve_feature_spec",
}


def python_files():
    ignored_parts = {".git", ".venv", "venv", "__pycache__"}

    for path in sorted(Path(".").rglob("*.py")):
        if any(part in ignored_parts for part in path.parts):
            continue
        yield path


def parse_imports(path):
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return []

    deps = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            deps.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            deps.append(node.module)

    return sorted(
        set(
            dep
            for dep in deps
            if dep.startswith("orchestrator") or dep in LOCAL_MODULES
        )
    )


def main():
    for path in python_files():
        deps = parse_imports(path)
        if not deps:
            continue

        print(f"\n{path}")
        for dep in deps:
            print(f"  -> {dep}")


if __name__ == "__main__":
    main()
