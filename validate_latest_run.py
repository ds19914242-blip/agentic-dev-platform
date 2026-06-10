from pathlib import Path
import subprocess

from orchestrator.product_registry import load_product_config
from orchestrator.run_status import write_status, append_event


def latest_run():
    runs = sorted(
        p for p in Path("runs").glob("feature-*")
        if p.is_dir()
    )

    if not runs:
        raise RuntimeError("No feature runs found")

    return runs[-1]


def run_command(command, cwd):
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
    )

    return result.returncode, result.stdout, result.stderr


def main():
    product_name = input("Product name: ").strip()

    product = load_product_config(product_name)
    repo_path = product["repo_path"]

    run_dir = latest_run()

    print(f"Validating run: {run_dir}")
    print(f"Using repo: {repo_path}")

    code, stdout, stderr = run_command(
        ["npx", "tsc", "--noEmit"],
        cwd=repo_path,
    )

    result = "passed" if code == 0 else "failed"

    validation_path = run_dir / "validation.md"

    validation_path.write_text(
        f"""# Validation Result

## Command

npx tsc --noEmit

## Result

{result}

## Exit Code

{code}

## STDOUT

{stdout}

## STDERR

{stderr}
"""
    )

    if code == 0:
        write_status(run_dir, "validated")
        append_event(run_dir, "Validation passed")
    else:
        write_status(run_dir, "validation_failed")
        append_event(run_dir, "Validation failed")

    print(f"Validation {result}: {validation_path}")


if __name__ == "__main__":
    main()
