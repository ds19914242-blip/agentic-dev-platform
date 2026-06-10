from orchestrator.work_item import WorkItem, WorkItemStatus


class Orchestrator:
    def create_work_item(self, work_item: WorkItem) -> WorkItem:
        print(f"[ORCHESTRATOR] Created work item: {work_item.title}")
        return work_item

    def start_planning(self, work_item: WorkItem) -> WorkItem:
        work_item.status = WorkItemStatus.PLANNING

        print(
            f"[ORCHESTRATOR] Planning started: {work_item.title}"
        )

        return work_item
