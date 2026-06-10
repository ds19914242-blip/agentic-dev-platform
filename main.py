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
