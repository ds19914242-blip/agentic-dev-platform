import py_compile
from pathlib import Path


IGNORED_PARTS = {".git", ".venv", "venv", "__pycache__"}


def python_files():
    for path in sorted(Path(".").rglob("*.py")):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        yield path


def main():
    files = list(python_files())
    failed = []

    for path in files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failed.append((path, exc))

    print(f"Checked Python files: {len(files)}")

    if failed:
        print()
        print("Failures:")
        for path, exc in failed:
            print(f"- {path}: {exc}")
        raise SystemExit(1)

    print("Architecture healthcheck passed.")


if __name__ == "__main__":
    main()
