from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class WorkItemType(str, Enum):
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    NEW_PRODUCT = "new_product"


class WorkItemStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkItem:
    title: str
    description: str
    type: WorkItemType
    status: WorkItemStatus = WorkItemStatus.CREATED
    created_at: str = datetime.utcnow().isoformat()
