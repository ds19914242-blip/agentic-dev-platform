import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from orchestrator.acceptance.runner import run_acceptance
from orchestrator.backlog_store import set_status
from orchestrator.product_registry import load_product_config


def _utc_now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _deployment_url(product):
    deployment = product.get("deployment") or {}
    acceptance = product.get("acceptance") or {}

    return (
        deployment.get("production_url")
        or acceptance.get("production_url")
        or acceptance.get("base_url")
        or ""
    )


def _check_url(url, timeout_seconds=20):
    try:
        request = Request(
            url,
            method="GET",
            headers={"User-Agent": "agentic-dev-platform-release-check"},
        )

        with urlopen(request, timeout=timeout_seconds) as response:
            return {
                "ok": 200 <= int(response.status) < 500,
                "status_code": int(response.status),
                "error": "",
            }

    except HTTPError as exc:
        return {
            "ok": 200 <= int(exc.code) < 500,
            "status_code": int(exc.code),
            "error": str(exc),
        }

    except URLError as exc:
        return {
            "ok": False,
            "status_code": None,
            "error": str(exc.reason),
        }

    except Exception as exc:
        return {
            "ok": False,
            "status_code": None,
            "error": str(exc),
        }


def _write_release_artifacts(task_path, product_name, production_url, url_result, acceptance_result):
    task_path = Path(task_path)
    epic_dir = task_path.parent

    json_path = epic_dir / "release-verification.json"
    md_path = epic_dir / "release-verification.md"

    acceptance_passed = bool(getattr(acceptance_result, "passed", False))
    passed = bool(url_result.get("ok")) and acceptance_passed

    payload = {
        "checked_at": _utc_now(),
        "task_path": str(task_path),
        "product": product_name,
        "production_url": production_url,
        "url_check": url_result,
        "acceptance": {
            "passed": acceptance_passed,
            "returncode": getattr(acceptance_result, "returncode", None),
            "command": getattr(acceptance_result, "command", ""),
        },
        "release_confirmed": passed,
    }

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Release Verification",
        "",
        f"- Product: {product_name}",
        f"- Task: `{task_path}`",
        f"- Production URL: {production_url}",
        f"- Checked at: {payload['checked_at']}",
        f"- URL check: {'passed' if url_result.get('ok') else 'failed'}",
        f"- HTTP status: {url_result.get('status_code')}",
        f"- Acceptance: {'passed' if acceptance_passed else 'failed'}",
        f"- Release confirmed: {'yes' if passed else 'no'}",
        "",
    ]

    if url_result.get("error"):
        md.extend(
            [
                "## URL Error",
                "",
                str(url_result.get("error")),
                "",
            ]
        )

    md_path.write_text("\n".join(md))

    return passed, md_path, json_path


def verify_production_release(task_path, product_name):
    product = load_product_config(product_name)
    production_url = _deployment_url(product)

    if not production_url:
        raise ValueError(f"production_url not configured for product: {product_name}")

    task_path = Path(task_path)
    epic_dir = task_path.parent

    set_status(task_path, "production_verification_running")

    url_result = _check_url(production_url)

    previous_base_url = os.environ.get("ACCEPTANCE_BASE_URL")
    os.environ["ACCEPTANCE_BASE_URL"] = production_url

    try:
        acceptance_result = run_acceptance(
            epic_dir=epic_dir,
            product_name=product_name,
        )
    finally:
        if previous_base_url is None:
            os.environ.pop("ACCEPTANCE_BASE_URL", None)
        else:
            os.environ["ACCEPTANCE_BASE_URL"] = previous_base_url

    passed, md_path, json_path = _write_release_artifacts(
        task_path=task_path,
        product_name=product_name,
        production_url=production_url,
        url_result=url_result,
        acceptance_result=acceptance_result,
    )

    set_status(task_path, "release_confirmed" if passed else "release_failed")

    return {
        "passed": passed,
        "production_url": production_url,
        "release_markdown": str(md_path),
        "release_json": str(json_path),
    }
