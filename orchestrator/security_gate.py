import json
from pathlib import Path


CRITICAL_RISK_PATTERNS = [
    ".env",
    "secret",
    "token",
    "billing",
    "payment",
    "stripe",
    "deploy",
    "docker",
    "vercel",
    "railway",
]

HIGH_RISK_PREFIXES = [
    "app/api/auth/",
    "app/login/",
]

HIGH_RISK_PATTERNS = [
    "permission",
    "role",
    "schema",
    "migration",
]

MEDIUM_RISK_PREFIXES = [
    "app/api/",
    "lib/",
    "src/",
]


def classify_file_risk(file):
    low = file.lower()

    if any(pattern in low for pattern in CRITICAL_RISK_PATTERNS):
        return "critical"

    if any(low.startswith(prefix) for prefix in HIGH_RISK_PREFIXES):
        return "high"

    if any(pattern in low for pattern in HIGH_RISK_PATTERNS):
        return "high"

    if low.startswith("app/") and low.endswith("/page.tsx"):
        return "low"

    if any(low.startswith(prefix) for prefix in MEDIUM_RISK_PREFIXES):
        return "medium"

    return "low"


def evaluate_security_gate(affected_files):
    risks = {
        "low": [],
        "medium": [],
        "high": [],
        "critical": [],
    }

    for file in affected_files:
        risk = classify_file_risk(file)
        risks[risk].append(file)

    if risks["critical"]:
        status = "blocked"
        reason = "Critical-risk files are affected."
    elif risks["high"]:
        status = "needs_approval"
        reason = "High-risk files are affected."
    elif risks["medium"]:
        status = "passed_with_warning"
        reason = "Medium-risk files are affected."
    else:
        status = "passed"
        reason = "Only low-risk files are affected."

    return {
        "status": status,
        "reason": reason,
        "risks": risks,
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

    for risk in ["critical", "high", "medium", "low"]:
        lines.append(f"## {risk.title()} Risk Files")
        lines.append("")

        files = result["risks"].get(risk, [])

        if files:
            for file in files:
                lines.append(f"- {file}")
        else:
            lines.append("_None_")

        lines.append("")

    return "\n".join(lines)


def write_security_report(run_dir, result):
    json_path = Path(run_dir) / "security-gate.json"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    md_path = Path(run_dir) / "security-gate.md"
    md_path.write_text(format_security_report(result))

    return md_path, result
