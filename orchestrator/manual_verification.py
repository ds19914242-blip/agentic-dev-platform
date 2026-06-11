import json
from pathlib import Path


def write_manual_verification(run_dir, feature, test_generation_text):
    run_dir = Path(run_dir)

    needs_manual = (
        "manual verification" in test_generation_text.lower()
        or "no automated tests will be generated" in test_generation_text.lower()
        or "test generation skipped" in test_generation_text.lower()
    )

    data = {
        "required": needs_manual,
        "reason": "Automated unit/e2e tests are unavailable for this task." if needs_manual else "",
    }

    (run_dir / "manual-verification.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False)
    )

    if needs_manual:
        (run_dir / "manual-verification.md").write_text(f"""# Manual Verification Required

Automated tests were not generated for this task.

## Feature

{feature}

## Required Manual Checks

Review `test-generation.md` and manually verify the scenarios listed there before treating this task as fully complete.

## Status

manual_verification_required
""")
    else:
        (run_dir / "manual-verification.md").write_text("""# Manual Verification

Manual verification is not required.
""")

    return needs_manual
