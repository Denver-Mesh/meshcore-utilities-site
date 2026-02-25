import enum
from typing import Optional

from pydantic import BaseModel

from backend.api.models.node_type import NodeType


class LetsMeshNodeRole(enum.Enum):
    """
    Enum representing the device role of a node in the LetsMesh network, as returned by the LetsMesh API.
    """
    COMPANION = 1
    REPEATER = 2
    ROOM = 3

    @classmethod
    def from_int(cls, role: int) -> 'LetsMeshNodeRole':
        if role == 1:
            return cls.COMPANION
        elif role == 2:
            return cls.REPEATER
        elif role == 3:
            return cls.ROOM
        else:
            raise ValueError(f"Unknown device role: {role}")

    @property
    def to_node_type(self) -> NodeType:
        if self == LetsMeshNodeRole.COMPANION:
            return NodeType.COMPANION
        elif self == LetsMeshNodeRole.REPEATER:
            return NodeType.REPEATER
        elif self == LetsMeshNodeRole.ROOM:
            return NodeType.ROOM_SERVER
        else:
            raise ValueError(f"Unknown device role: {self.value}")


class LetsMeshNodeLocation(BaseModel):
    """
    Represents the location of a node as returned by the LetsMesh API.
    """
    latitude: float
    longitude: float


class LetsMeshNode(BaseModel):
    """
    Represents a node as returned by the LetsMesh API.
    """
    public_key: str
    name: str
    device_role: LetsMeshNodeRole
    regions: list[str]
    first_seen: str  # ISO 8601 timestamp
    last_seen: str  # ISO 8601 timestamp
    is_mqtt_connected: bool
    location: Optional[LetsMeshNodeLocation] = None
