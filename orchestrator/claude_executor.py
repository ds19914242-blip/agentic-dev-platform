import subprocess
import time
from orchestrator.llm_metrics import increment_model_calls
from pathlib import Path


RETRYABLE_ERRORS = [
    "socket connection was closed",
    "connection was closed",
    "network",
    "timeout",
    "temporarily unavailable",
    "rate limit",
    "overloaded",
]


def is_retryable_error(output, error):
    text = f"{output}\n{error}".lower()
    return any(pattern in text for pattern in RETRYABLE_ERRORS)


def run_claude(repo_path, prompt, allow_writes=False, max_turns=15, retries=2):
    command = ["claude", "--print", "--max-turns", str(max_turns)]

    if allow_writes:
        command.append("--dangerously-skip-permissions")

    command.append(prompt)

    last_output = ""
    last_error = ""

    for attempt in range(retries + 1):
        increment_model_calls()

        result = subprocess.run(
            command,
            cwd=repo_path,
            text=True,
            capture_output=True,
        )

        output = result.stdout or ""
        error = result.stderr or ""

        last_output = output
        last_error = error

        if result.returncode == 0:
            return output

        if "Reached max turns" in output:
            return output + "\n\n[WARNING] Claude reached max turns before final response."

        if attempt < retries and is_retryable_error(output, error):
            sleep_seconds = 3 * (attempt + 1)
            print(f"Claude retryable failure, retrying in {sleep_seconds}s...")
            time.sleep(sleep_seconds)
            continue

        raise RuntimeError(
            f"Claude failed with code {result.returncode}\nSTDERR:\n{error}\nSTDOUT:\n{output}"
        )

    raise RuntimeError(
        f"Claude failed after retries\nSTDERR:\n{last_error}\nSTDOUT:\n{last_output}"
    )


def run_claude_from_file(repo_path, prompt_path, allow_writes=False, max_turns=15, retries=2):
    prompt = Path(prompt_path).read_text()

    max_chars = 50000

    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "\n\n[TRUNCATED BY AGENTIC DEV PLATFORM]\n"

    return run_claude(
        repo_path,
        prompt,
        allow_writes=allow_writes,
        max_turns=max_turns,
        retries=retries,
    )
