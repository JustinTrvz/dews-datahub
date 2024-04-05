from enum import Enum


class Status(Enum):
    DONE = "done"
    IN_PROGRESS = "in progress"
    FAILED = "failed"