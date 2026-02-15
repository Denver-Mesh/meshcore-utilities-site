import enum
from abc import abstractmethod, ABC
from typing import Optional

import objectrest
from pydantic import BaseModel

from utils import is_reserved_public_key_id

MESHMAPPER_REPEATERS_URL = "https://den.meshmapper.net/api.php?request=repeaters"  # Just repeaters/room servers in Denver
LETSMESH_NODES_URL = "https://api.letsmesh.net/api/nodes?region=DEN"  # All devices in Denver


class BaseNode(BaseModel, ABC):
    pass

    @abstractmethod
    def public_key_id(self) -> str:
        """
        Return the first byte (2-character hex string) of the public key, which is used as an identifier for the node.
        :return: The first byte of the public key as a hex string.
        :rtype: str
        """
        raise NotImplementedError("Subclasses must implement the public_key_id property")


class NodeType(enum.Enum):
    REPEATER = 1
    ROOM_SERVER = 2
    COMPANION = 3

    @classmethod
    def from_letsmesh_role(cls, role: int) -> 'NodeType':
        if role == 1:
            return cls.REPEATER
        elif role == 2:
            return cls.ROOM_SERVER
        elif role == 3:
            return cls.COMPANION
        else:
            raise ValueError(f"Unknown device role: {role}")


class Node(BaseNode):
    """
    Internal representation of a node, which can be either a LetsMeshNode or a MeshMapperRepeater.
    Used for processing and comparing nodes from both sources.
    """
    public_key: str
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    node_type: NodeType
    is_observer: bool = False

    @property
    def public_key_id(self) -> str:
        """
        Return the first byte (2-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The first byte of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key[:2].upper()


class MeshMapperRepeater(BaseModel):
    id: str
    hex_id: str
    name: str
    lat: float
    lon: float
    last_heard: int
    created_at: str
    enabled: int
    power: str
    iata: str
    can_reach: str | None
    notes: str | None
    locked: int


class LetsMeshNodeLocation(BaseModel):
    latitude: float
    longitude: float


class LetsMeshNode(BaseModel):
    public_key: str
    name: str
    device_role: int
    regions: list[str]
    first_seen: str
    last_seen: str
    is_mqtt_connected: bool
    location: Optional[LetsMeshNodeLocation] = None


def _compare_public_key_ids(id_1: str, id_2: str) -> bool:
    """
    Compare two public key IDs (the first byte of the public key) to determine if they conflict.
    Two public key IDs conflict if they are the same (case-insensitive).
    :param id_1: The first public key ID to compare.
    :type id_1: str
    :param id_2: The second public key ID to compare.
    :type id_2: str
    :return: True if the public key IDs conflict, False otherwise.
    :rtype: bool
    """
    return id_1.upper() == id_2.upper()


def _id_exists_in_list(id_: str, ids_to_track: list[str]) -> bool:
    """
    Check if a public key ID exists in a list of public key IDs (case-insensitive).
    :param id_: The public key ID to check for existence in the list.
    :type id_: str
    :param ids_to_track: The list of public key IDs to check against.
    :type ids_to_track: list[str]
    :return: True if the public key ID exists in the list, False otherwise.
    :rtype: bool
    """
    return any(_compare_public_key_ids(id_1=id_, id_2=existing_id) for existing_id in ids_to_track)


def get_denver_nodes() -> list[Node]:
    """
    Get all nodes in the Denver region from the LetsMesh API (repeaters, room servers, and companions)
    :return: A list of Node objects representing all nodes in the Denver region.
    :rtype: list[Node]
    """
    letsmesh_nodes: list[LetsMeshNode] = objectrest.get_object(url=LETSMESH_NODES_URL,  # type: ignore
                                                               model=LetsMeshNode,
                                                               extract_list=True,
                                                               sub_keys=["nodes"],
                                                               headers={
                                                                   "Host": "api.letsmesh.net",
                                                                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0",
                                                                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                                                   "Accept-Language": "en-US,en;q=0.9",
                                                                   "Accept-Encoding": "gzip, deflate, br, zstd",
                                                                   "Connection": "keep-alive",
                                                               })
    return [
        Node(
            public_key=node.public_key,
            name=node.name,
            latitude=node.location.latitude if node.location else None,
            longitude=node.location.longitude if node.location else None,
            node_type=NodeType.from_letsmesh_role(node.device_role),
            is_observer=not node.is_mqtt_connected
        )
        for node in letsmesh_nodes
    ]


def get_denver_repeaters() -> list[Node]:
    """
    Get all repeaters/room servers in the Denver region from the MeshMapper API.
    :return: A list of Node objects representing all repeaters/room servers in the Denver region.
    :rtype: list[Node]
    """
    meshmapper_repeaters: list[MeshMapperRepeater] = objectrest.get_object(url=MESHMAPPER_REPEATERS_URL,  # type: ignore
                                                                           model=MeshMapperRepeater,
                                                                           extract_list=True)
    return [
        Node(
            public_key=repeater.hex_id,
            name=repeater.name,
            latitude=repeater.lat,
            longitude=repeater.lon,
            node_type=NodeType.REPEATER,
            is_observer=False  # Unknown
        )
        for repeater in meshmapper_repeaters
    ]


def get_conflicting_repeaters(public_key_id: str) -> list[Node]:
    """
    Get all repeaters/room servers that conflict with the provided public key ID.
    :return: A list of Node objects representing all repeaters/room servers that conflict with the provided public key ID.
    :rtype: list[Node]
    """
    repeaters = get_denver_repeaters()
    return [repeater for repeater in repeaters if
            _compare_public_key_ids(id_1=repeater.public_key_id, id_2=public_key_id)]


def get_conflicting_nodes(public_key_id: str) -> list[Node]:
    """
    Get all nodes (regardless of type) that conflict with the provided public key ID.
    :return: A list of Node objects representing all nodes that conflict with the provided public key ID.
    :rtype: list[Node]
    """
    nodes = get_denver_nodes()
    return [node for node in nodes if _compare_public_key_ids(id_1=node.public_key_id, id_2=public_key_id)]


def suggest_public_key_id() -> str:
    """
    Suggest a new public key ID that is not currently in use.
    :return: A suggested public key ID that is not currently in use.
    :rtype: str
    """
    nodes: list[Node] = get_denver_nodes()
    used_public_key_ids: set[str] = set(node.public_key_id for node in nodes)

    # Iterate through all possible public key IDs (00 to FF) and return the first one that is not in use
    for i in range(256):
        public_key_id = f"{i:02x}"
        if is_reserved_public_key_id(public_key_id):
            continue
        if not _id_exists_in_list(id_=public_key_id, ids_to_track=list(used_public_key_ids)):
            return public_key_id

    raise RuntimeError("No available public key IDs found")
