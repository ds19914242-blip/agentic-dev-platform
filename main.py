# DEPRECATED ENTRYPOINT
#
# This file belongs to an older workflow path.
# It is kept temporarily for compatibility while the v0.4 architecture stabilizes.
# Do not extend this file. Prefer agentic.py + orchestrator/workflows + orchestrator/services.
#

from orchestrator.work_item import (
    WorkItem,
    WorkItemType,
)

from orchestrator.orchestrator import Orchestrator


def main():
    orchestrator = Orchestrator()

    item = WorkItem(
        title="Add AI summaries",
        description="Generate AI summaries for RSS items",
        type=WorkItemType.FEATURE,
    )

    orchestrator.create_work_item(item)

    orchestrator.start_planning(item)

    print()
    print(item)


if __name__ == "__main__":
    main()
