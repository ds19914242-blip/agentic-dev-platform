SENSITIVE_PATTERNS = [
    "auth",
    "login",
    "session",
    "secret",
    "billing",
    "payment",
    "stripe",
    "schema",
    "migration",
    ".env",
    "deploy",
    "vercel",
    "railway",
    "docker",
]


def evaluate_security_gate(affected_files):
    sensitive = []

    for file in affected_files:
        low = file.lower()
        if any(pattern in low for pattern in SENSITIVE_PATTERNS):
            sensitive.append(file)

    if sensitive:
        return {
            "status": "needs_approval",
            "reason": "Sensitive files may be affected.",
            "files": sensitive,
        }

    return {
        "status": "passed",
        "reason": "No sensitive files detected.",
        "files": [],
    }


def format_security_report(result):
    lines = ["# Security Gate", ""]
    lines.append("## Status")
    lines.append("")
    lines.append(result["status"])
    lines.append("")
    lines.append("## Reason")
    lines.append("")
    lines.append(result["reason"])
    lines.append("")
    lines.append("## Sensitive Files")
    lines.append("")

    if result["files"]:
        for file in result["files"]:
            lines.append(f"- {file}")
    else:
        lines.append("_None_")

    return "\n".join(lines)
