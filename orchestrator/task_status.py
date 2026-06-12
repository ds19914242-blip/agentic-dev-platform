from enum import Enum


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    BLOCKED_HUMAN_REVIEW = "blocked_human_review"

    PR_CREATED = "pr_created"
    MERGED = "merged"

    DONE = "done"
    DONE_NO_PR = "done_no_pr"

    ALREADY_SATISFIED = "already_satisfied"
    NO_CHANGES_NEEDED = "no_changes_needed"

    MANUAL_VERIFICATION_REQUIRED = "manual_verification_required"
    MANUAL_VERIFICATION_PASSED = "manual_verification_passed"
    MANUAL_VERIFICATION_FAILED = "manual_verification_failed"


ORDERED_STATUSES = [
    status.value
    for status in [
        TaskStatus.MERGED,
        TaskStatus.PR_CREATED,
        TaskStatus.DONE,
        TaskStatus.DONE_NO_PR,
        TaskStatus.ALREADY_SATISFIED,
        TaskStatus.NO_CHANGES_NEEDED,
        TaskStatus.MANUAL_VERIFICATION_REQUIRED,
        TaskStatus.MANUAL_VERIFICATION_PASSED,
        TaskStatus.MANUAL_VERIFICATION_FAILED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.BLOCKED,
        TaskStatus.BLOCKED_HUMAN_REVIEW,
        TaskStatus.TODO,
    ]
]

ACTIVE_STATUSES = {
    TaskStatus.TODO.value,
    TaskStatus.BLOCKED.value,
    TaskStatus.MANUAL_VERIFICATION_FAILED.value,
}

SKIP_STATUSES = {
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.PR_CREATED.value,
    TaskStatus.MERGED.value,
    TaskStatus.MANUAL_VERIFICATION_PASSED.value,
}

COMPLETED_STATUSES = {
    TaskStatus.MERGED.value,
    TaskStatus.PR_CREATED.value,
    TaskStatus.DONE.value,
    TaskStatus.DONE_NO_PR.value,
    TaskStatus.ALREADY_SATISFIED.value,
    TaskStatus.NO_CHANGES_NEEDED.value,
    TaskStatus.MANUAL_VERIFICATION_PASSED.value,
}


def normalize_status(value):
    if not value:
        return TaskStatus.TODO.value

    status = value.strip().lower()

    valid = {item.value for item in TaskStatus}

    if status in valid:
        return status

    return TaskStatus.TODO.value
