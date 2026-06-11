from pathlib import Path

from orchestrator.memory_store import (
    load_product_memory,
    load_run_memory,
    load_architecture_memory,
)


def find_related_runs(feature, runs, limit=5):
    feature_terms = {
        token.lower().strip(".,:;()[]{}")
        for token in feature.split()
        if len(token.strip(".,:;()[]{}")) >= 4
    }

    scored = []
    for run in runs:
        request = run.get("request") or ""
        request_terms = {
            token.lower().strip(".,:;()[]{}")
            for token in request.split()
            if len(token.strip(".,:;()[]{}")) >= 4
        }

        overlap = len(feature_terms & request_terms)
        if overlap:
            scored.append((overlap, run))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [run for _, run in scored[:limit]]


def build_memory_context(product_name, feature):
    product_memory = load_product_memory(product_name)
    run_memory = load_run_memory(product_name)
    architecture_memory = load_architecture_memory(product_name)
    related_runs = find_related_runs(feature, run_memory)

    lines = [
        "# Platform Memory Context",
        "",
        "## Product Memory",
        "",
    ]

    if product_memory:
        for key, value in product_memory.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("_No product memory recorded yet._")

    lines.extend([
        "",
        "## Architecture Memory",
        "",
    ])

    if architecture_memory:
        for item in architecture_memory[-10:]:
            decision = item.get("decision", "")
            reason = item.get("reason", "")
            lines.append(f"- {decision} — {reason}")
    else:
        lines.append("_No architecture decisions recorded yet._")

    lines.extend([
        "",
        "## Related Previous Runs",
        "",
    ])

    if related_runs:
        for run in related_runs:
            lines.append(
                f"- {run.get('run_id')}: {run.get('request')} "
                f"(status={run.get('status')}, validation={run.get('validation_result')})"
            )
    else:
        lines.append("_No related previous runs found._")

    lines.append("")
    return "\n".join(lines)


def write_memory_context(run_dir, product_name, feature):
    run_dir = Path(run_dir)
    content = build_memory_context(product_name, feature)
    path = run_dir / "memory-context.md"
    path.write_text(content)
    return path, content
