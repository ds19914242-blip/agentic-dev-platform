LOW_RISK_PREFIXES = [
    "components/",
    "app/",
]

MEDIUM_RISK_PREFIXES = [
    "app/api/",
    "lib/",
    "src/",
]

HIGH_RISK_PATTERNS = [
    "auth",
    "login",
    "session",
    "permission",
    "role",
    "database",
    "db",
    "schema",
    "migration",
]

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


def classify_file_risk(file):
    low = file.lower()

    if any(pattern in low for pattern in CRITICAL_RISK_PATTERNS):
        return "critical"

    if any(pattern in low for pattern in HIGH_RISK_PATTERNS):
        return "high"

    if any(low.startswith(prefix) for prefix in MEDIUM_RISK_PREFIXES):
        return "medium"

    if any(low.startswith(prefix) for prefix in LOW_RISK_PREFIXES):
        return "low"

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
