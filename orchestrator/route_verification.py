import json
import re
from datetime import datetime
from pathlib import Path

from orchestrator.outcome_store import attach_evidence


ROUTE_RE = re.compile(r'["`](/(?!api/)[a-zA-Z0-9_./-]*)["`]')
API_ROUTE_RE = re.compile(r'["`](/api/[a-zA-Z0-9_./-]*)["`]')


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _read(path):
    path = Path(path)
    return path.read_text(errors="ignore") if path.exists() else ""


def _route_to_page_path(repo_path, route):
    route = route.strip("/")
    if not route:
        return Path(repo_path) / "app" / "page.tsx"
    return Path(repo_path) / "app" / route / "page.tsx"


def _api_route_to_path(repo_path, route):
    route = route.strip("/")
    if route.startswith("api/"):
        route = route[len("api/"):]
    return Path(repo_path) / "app" / "api" / route / "route.ts"


def _is_speculative_route(text, route):
    lowered = text.lower()
    route_lower = route.lower()

    for match in re.finditer(re.escape(route_lower), lowered):
        start = max(0, match.start() - 120)
        end = min(len(lowered), match.end() + 120)
        context = lowered[start:end]

        has_alternative_word = (
            " or " in context
            or " или " in context
            or "например" in context
            or "e.g." in context
            or "such as" in context
        )

        other_routes = [
            candidate
            for candidate in ROUTE_RE.findall(context)
            if candidate.lower() != route_lower
        ]

        if has_alternative_word and other_routes:
            return True

    return False


def extract_expected_routes(text):
    routes = sorted(set(ROUTE_RE.findall(text)))
    return [
        r for r in routes
        if not _looks_external_or_asset(r)
        and not _is_speculative_route(text, r)
    ]


def extract_expected_api_routes(text):
    return sorted(set(API_ROUTE_RE.findall(text)))


def _looks_external_or_asset(route):
    return (
        route.startswith("//")
        or "." in Path(route).name
        or route.startswith("/_next")
    )


def collect_route_mentions(epic_dir):
    epic_dir = Path(epic_dir)
    chunks = []

    for name in [
        "product-spec.md",
        "feature-spec.md",
        "acceptance-scenarios.md",
    ]:
        chunks.append(_read(epic_dir / name))

    for task in sorted(epic_dir.glob("task-*.md")):
        chunks.append(_read(task))

    text = "\n\n".join(chunks)

    return {
        "routes": extract_expected_routes(text),
        "api_routes": extract_expected_api_routes(text),
    }


def verify_routes(epic_dir, repo_path):
    mentions = collect_route_mentions(epic_dir)

    route_checks = []
    for route in mentions["routes"]:
        page_path = _route_to_page_path(repo_path, route)
        route_checks.append(
            {
                "route": route,
                "expected_file": str(page_path),
                "exists": page_path.exists(),
            }
        )

    api_checks = []
    for route in mentions["api_routes"]:
        api_path = _api_route_to_path(repo_path, route)
        api_checks.append(
            {
                "route": route,
                "expected_file": str(api_path),
                "exists": api_path.exists(),
            }
        )

    missing = [
        check for check in route_checks + api_checks
        if not check["exists"]
    ]

    return {
        "schema": "route_verification_v1",
        "verified_at": now_iso(),
        "result": "passed" if not missing else "failed",
        "routes": route_checks,
        "api_routes": api_checks,
        "missing": missing,
    }


def write_route_verification(epic_dir, result):
    epic_dir = Path(epic_dir)

    json_path = epic_dir / "route-verification.json"
    md_path = epic_dir / "route-verification.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    attach_evidence(epic_dir, "route_verification", "route-verification.json")

    lines = [
        "# Route Verification",
        "",
        "## Result",
        "",
        result["result"],
        "",
        "## Missing Routes",
        "",
    ]

    if not result["missing"]:
        lines.append("_None_")
    else:
        for item in result["missing"]:
            lines.append(f"- `{item['route']}` expected `{item['expected_file']}`")

    lines.extend(["", "## Page Routes", ""])

    if not result["routes"]:
        lines.append("_No page route mentions found._")
    else:
        for item in result["routes"]:
            status = "OK" if item["exists"] else "MISSING"
            lines.append(f"- {status}: `{item['route']}` → `{item['expected_file']}`")

    lines.extend(["", "## API Routes", ""])

    if not result["api_routes"]:
        lines.append("_No API route mentions found._")
    else:
        for item in result["api_routes"]:
            status = "OK" if item["exists"] else "MISSING"
            lines.append(f"- {status}: `{item['route']}` → `{item['expected_file']}`")

    lines.extend(["", "## Verified At", "", result["verified_at"], ""])

    md_path.write_text("\n".join(lines))
    attach_evidence(epic_dir, "route_verification_report", "route-verification.md")
    return md_path, json_path
