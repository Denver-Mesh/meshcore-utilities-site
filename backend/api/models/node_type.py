import enum


class NodeType(enum.Enum):
    """
    Enum representing the type of given node, used throughout the logic here
    """
    REPEATER = 1
    ROOM_SERVER = 2
    COMPANION = 3
    ROOM_OR_REPEATER = 4  # Used when we can't be sure if it's a room server or repeater, but we know it's one of those two

    @classmethod
    def from_int(cls, role: int) -> 'NodeType':
        if role == 1:
            return cls.REPEATER
        elif role == 2:
            return cls.ROOM_SERVER
        elif role == 3:
            return cls.COMPANION
        elif role == 4:
            return cls.ROOM_OR_REPEATER
        else:
            raise ValueError(f"Unknown device role: {role}")
