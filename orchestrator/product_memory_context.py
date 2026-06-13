import json

from orchestrator.memory_store import load_product_memory, load_run_memory


def _safe_list(value):
    return value if isinstance(value, list) else []


def format_product_memory(product_name):
    memory = load_product_memory(product_name)
    runs = load_run_memory(product_name)[-10:]

    if not memory and not runs:
        return "No product memory found."

    lines = [
        "# Product Memory",
        "",
        f"Product: {product_name}",
        "",
        "## Stable Context",
        "",
    ]

    for key in [
        "name",
        "type",
        "status",
        "framework",
        "vision",
        "primary_users",
        "known_constraints",
        "product_principles",
        "current_focus",
    ]:
        if key in memory:
            value = memory[key]
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            lines.append(f"### {key}")
            lines.append(str(value))
            lines.append("")

    capabilities = memory.get("capabilities")
    if capabilities:
        lines.append("## Capabilities")
        lines.append(json.dumps(capabilities, ensure_ascii=False, indent=2))
        lines.append("")

    validators = memory.get("validators")
    if validators:
        lines.append("## Validators")
        lines.append(json.dumps(validators, ensure_ascii=False, indent=2))
        lines.append("")

    lines.append("## Recent Runs")
    lines.append("")

    if not runs:
        lines.append("No recent runs recorded.")
    else:
        for run in runs:
            lines.append(
                "- "
                + " | ".join(
                    str(part)
                    for part in [
                        run.get("run_id", "unknown"),
                        run.get("request", ""),
                        run.get("status", ""),
                        run.get("validation_result", ""),
                    ]
                    if part
                )
            )

    return "\n".join(lines).strip() + "\n"
