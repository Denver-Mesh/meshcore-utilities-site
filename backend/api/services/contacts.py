import enum
from datetime import datetime, timedelta
from typing import Optional

from coloradomesh.meshcore.models.general import Node, NodeType
from coloradomesh.meshcore.services.nodes import get_colorado_nodes


class ContactsOrder(enum.Enum):
    """
    Have been heard
    """
    RECENT = "recent"
    """
    Have been heard most recently.
    """
    OLDEST = "oldest"
    """
    Were first heard the most long ago.
    """
    NEWEST = "newest"
    """
    Were first heard the most recently.
    """
    ALPHABETICAL = "alpha"
    """
    Alphabetical by name.
    """
    IDENTITY = "identity"
    """
    Alphabetical by ID.
    """
    # POPULAR = "popular"
    """
    Have been heard the most.
    """


class ContactsStatus(enum.Enum):
    ACTIVE = "active"
    """
    Only nodes that are active.
    """
    ALL = "all"
    """
    All nodes
    """


class ContactsType(enum.Enum):
    REPEATERS = "repeaters"
    ROOMS = "rooms"
    COMPANIONS = "companions"
    REPEATERS_AND_ROOMS = "repeaters_and_rooms"
    ALL = "all"


def _sort_nodes(nodes: list[Node], _order: Optional[ContactsOrder]) -> list[Node]:
    if not _order:
        return nodes

    match _order:
        case ContactsOrder.RECENT.value:
            return sorted(nodes, key=lambda n: n.last_heard)
        case ContactsOrder.OLDEST.value:
            return sorted(nodes, key=lambda n: n.created_at)
        case ContactsOrder.NEWEST.value:
            return sorted(nodes, key=lambda n: n.created_at, reverse=True)
        case ContactsOrder.ALPHABETICAL.value:
            return sorted(nodes, key=lambda n: n.name)
        case ContactsOrder.IDENTITY.value:
            return sorted(nodes, key=lambda n: n.public_key)
        # case ContactsOrder.POPULAR.value:

    return nodes


def _filter_nodes_by_type(nodes: list[Node], _type: Optional[ContactsType]) -> list[Node]:
    if not _type:
        return nodes

    match _type:
        case ContactsType.REPEATERS.value:
            return [node for node in nodes if node.node_type == NodeType.REPEATER]
        case ContactsType.ROOMS.value:
            return [node for node in nodes if node.node_type == NodeType.ROOM_SERVER]
        case ContactsType.REPEATERS_AND_ROOMS.value:
            return [node for node in nodes if node.node_type in (NodeType.REPEATER, NodeType.ROOM_SERVER)]
        case ContactsType.COMPANIONS.value:
            return [node for node in nodes if node.node_type == NodeType.COMPANION]
        case ContactsType.ALL.value:
            return nodes

    return nodes


def _node_heard_since(node: Node, timestamp: float) -> bool:
    """
    Determine if a node was heard since the given timestamp.
    :param node: The node to check.
    :param timestamp: The timestamp to check.
    :return: True if the node was heard since the given timestamp, False otherwise.
    """
    if not node.last_heard:
        return False

    return node.last_heard >= timestamp


def _filter_nodes_by_status(nodes: list[Node], _status: Optional[ContactsStatus]) -> list[Node]:
    if not _status:
        return nodes

    _72_hours_ago_timestamp: float = (datetime.now() - timedelta(hours=72)).timestamp()

    match _status:
        case ContactsStatus.ACTIVE.value:
            return [node for node in nodes if _node_heard_since(node, timestamp=_72_hours_ago_timestamp)]
        case ContactsStatus.ALL.value:
            return nodes

    return nodes


def _concat_nodes(nodes: list[Node], length: Optional[int]) -> list[Node]:
    if not length:
        return nodes

    return nodes[:length]


def prepare_contacts(count: int,
                     order: Optional[ContactsOrder],
                     status: Optional[ContactsStatus],
                     _type: Optional[ContactsType]) -> dict:
    """
    Prepare a JSON object containing contacts in Colorado.
    """
    nodes: list[Node] = get_colorado_nodes()
    # Filter, sort, then concatenate
    nodes = _filter_nodes_by_status(nodes=nodes, _status=status)
    nodes = _filter_nodes_by_type(nodes=nodes, _type=_type)
    nodes = _sort_nodes(nodes=nodes, _order=order)
    nodes = _concat_nodes(nodes=nodes, length=count)

    contacts = []
    for node in nodes:
        contacts.append({
            "type": node.node_type.value,
            "name": node.name,
            "custom_name": None,
            "public_key": node.public_key,
            "flags": 0,
            # needs to be strings
            "latitude": str(node.latitude),
            "longitude": str(node.longitude),
            "last_advert": node.last_heard,
            "last_modified": node.last_heard,
            "out_path": None,
        })
    return {"contacts": contacts}
