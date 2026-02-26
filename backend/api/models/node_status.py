import enum


class NodeStatus(enum.Enum):
    """
    Enum representing the status of given node, used throughout the logic here
    """
    NEW = 0
    ACTIVE = 1
    STALE = 2
    UNKNOWN = 2

    @classmethod
    def from_int(cls, status: int) -> 'NodeStatus':
        if status == 1:
            return cls.ACTIVE
        elif status == 2:
            return cls.UNKNOWN
        else:
            raise ValueError(f"Unknown device status: {status}")

    def to_str(self) -> str:
        if self == NodeStatus.NEW:
            return "new"
        elif self == NodeStatus.ACTIVE:
            return "active"
        elif self == NodeStatus.STALE:
            return "stale"
        elif self == NodeStatus.UNKNOWN:
            return "unknown"
        else:
            raise ValueError(f"Unknown device status: {self.value}")

