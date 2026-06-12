import argparse
import re
from datetime import datetime
from pathlib import Path


RESULT_BLOCK_RE = re.compile(
    r"\n## Manual Verification Result\n\n.*?(?=\n## |\Z)",
    flags=re.DOTALL,
)


def upsert_status(text, status):
    if re.search(r"^Status:", text, flags=re.MULTILINE):
        return re.sub(r"^Status:.*$", f"Status: {status}", text, flags=re.MULTILINE)

    return f"Status: {status}\n\n{text}"


def remove_previous_result_blocks(text):
    while RESULT_BLOCK_RE.search(text):
        text = RESULT_BLOCK_RE.sub("", text)

    return text.rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_path")
    parser.add_argument("--failed", action="store_true")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    path = Path(args.task_path)

    if not path.exists():
        raise SystemExit(f"Task not found: {path}")

    status = "manual_verification_failed" if args.failed else "manual_verification_passed"
    note = args.note or (
        "Manual verification failed."
        if args.failed
        else "Manual verification passed."
    )
    timestamp = datetime.now().isoformat(timespec="seconds")

    text = path.read_text(errors="ignore")
    text = upsert_status(text, status)
    text = remove_previous_result_blocks(text)

    text += f"""
## Manual Verification Result

Status: {status}
Verified At: {timestamp}
Note: {note}
"""

    path.write_text(text)
    print(f"{path} marked {status}")


if __name__ == "__main__":
    main()
