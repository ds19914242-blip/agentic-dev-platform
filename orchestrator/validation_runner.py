import json
import subprocess
from pathlib import Path

from orchestrator.run_status import append_event


def run_validator(command, cwd):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            shell=True,
            timeout=180,
        )

        return {
            "command": command,
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": False,
        }

    except subprocess.TimeoutExpired as err:
        return {
            "command": command,
            "exit_code": None,
            "passed": False,
            "stdout": err.stdout or "",
            "stderr": err.stderr or "",
            "timed_out": True,
        }


def run_validators(repo_path, validators):
    results = []

    for validator in validators:
        required = bool(validator.get("required", True))

        result = run_validator(validator["command"], repo_path)

        results.append({
            "name": validator["name"],
            "required": required,
            **result,
        })

    return results


def write_validation_report(run_dir, results):
    required_results = [r for r in results if r["required"]]
    all_required_passed = all(r["passed"] for r in required_results) if required_results else False

    data = {
        "overall_result": "passed" if all_required_passed else "failed",
        "validators": results,
    }

    json_path = Path(run_dir) / "validation.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    lines = ["# Validation Result", ""]

    lines.append("## Overall Result")
    lines.append("")
    lines.append(data["overall_result"])
    lines.append("")

    if not results:
        lines.append("## Validators")
        lines.append("")
        lines.append("_No validators configured_")
        lines.append("")

    for result in results:
        lines.append(f"## {result['name']}")
        lines.append("")
        lines.append(f"Required: {result['required']}")
        lines.append("")
        lines.append(f"Command: `{result['command']}`")
        lines.append("")
        lines.append(f"Result: {'passed' if result['passed'] else 'failed'}")
        lines.append("")
        lines.append(f"Timed Out: {result['timed_out']}")
        lines.append("")
        lines.append(f"Exit Code: {result['exit_code']}")
        lines.append("")
        lines.append("### STDOUT")
        lines.append("")
        lines.append("```text")
        lines.append(result["stdout"])
        lines.append("```")
        lines.append("")
        lines.append("### STDERR")
        lines.append("")
        lines.append("```text")
        lines.append(result["stderr"])
        lines.append("```")
        lines.append("")

    md_path = Path(run_dir) / "validation.md"
    md_path.write_text("\n".join(lines))

    try:
        append_event(
            run_dir,
            f"Validation report written: {'passed' if all_required_passed else 'failed'}",
        )
    except Exception:
        pass

    return md_path, all_required_passed
