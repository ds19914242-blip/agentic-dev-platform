from pathlib import Path
import subprocess


def read_task(epic_path, task_number):
    task_path = Path(epic_path) / f"task-{task_number:03d}.md"

    if not task_path.exists():
        raise FileNotFoundError(f"Task not found: {task_path}")

    return task_path, task_path.read_text()


def run_autonomous(product_name, task_text):
    input_text = f"{product_name}\n{task_text}\n"

    result = subprocess.run(
        ["python3", "run_autonomous_feature.py"],
        input=input_text,
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Epic task run failed")


def main():
    product_name = input("Product name: ").strip()
    epic_path = input("Epic path: ").strip()
    task_number = int(input("Task number: ").strip())

    task_path, task_text = read_task(epic_path, task_number)

    print(f"Running epic task: {task_path}")
    print()

    run_autonomous(product_name, task_text)


if __name__ == "__main__":
    main()
