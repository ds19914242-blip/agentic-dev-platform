import re
from pathlib import Path


IMPORT_RE = re.compile(r'(?:import .* from ["\\\'](.+)["\\\']|import\\(["\\\'](.+)["\\\']\\))')


def analyze_imports(repo_path, files):
    result = {}

    for file in files:
        path = Path(repo_path) / file

        if not path.exists() or not path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            continue

        imports = []

        for match in IMPORT_RE.findall(path.read_text(errors="ignore")):
            value = match[0] or match[1]
            imports.append(value)

        if imports:
            result[file] = imports

    return result


def format_import_map(imports):
    lines = ["# Import Map", ""]

    if not imports:
        lines.append("_No imports detected_")
        return "\n".join(lines)

    for file, values in imports.items():
        lines.append(f"## {file}")
        lines.append("")
        for value in values[:30]:
            lines.append(f"- {value}")
        lines.append("")

    return "\n".join(lines)
