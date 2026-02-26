from urllib.parse import quote

import objectrest

from backend.api.models.letsmesh_node import LetsMeshNode
from backend.api.models.node import Node
from backend.api.services.name_generator import is_reserved_public_key_id
from backend.modules import utils

DENVER_REPEATERS_DATA = "https://raw.githubusercontent.com/Denver-Mesh/docs/refs/heads/master/MeshCore/nodes/repeaters.json"
# DENVER_COMPANIONS_DATA = "https://raw.githubusercontent.com/Denver-Mesh/docs/refs/heads/master/MeshCore/nodes/companions.json"
LETSMESH_NODES_URL = "https://api.letsmesh.net/api/nodes?region=DEN"  # All devices in Denver


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


def _build_contact_url(name: str, public_key: str) -> str:
    encoded_name = quote(name)
    return f"meshcore://contact/add?name={encoded_name}&public_key={public_key.upper()}&type=2"


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
            node_type=node.device_role.to_node_type,
            is_observer=not node.is_mqtt_connected,
            contact=_build_contact_url(name=node.name, public_key=node.public_key),
            created_at=utils.iso8601_to_unix_timestamp(node.first_seen),
            last_heard=utils.iso8601_to_unix_timestamp(node.last_seen),
        )
        for node in letsmesh_nodes
    ]


def get_denver_repeaters() -> list[Node]:
    """
    Get all repeaters/room servers in the Denver region from the MeshMapper snapshot.
    :return: A list of Node objects representing all repeaters/room servers in the Denver region.
    :rtype: list[Node]
    """
    nodes: list[Node] = objectrest.get_object(url=DENVER_REPEATERS_DATA,  # type: ignore
                                              model=Node,
                                              extract_list=True)
    return nodes


def get_conflicting_repeaters(public_key_id: str) -> list[Node]:
    """
    Get all repeaters/room servers that conflict with the provided public key ID.
    :return: A list of Node objects representing all repeaters/room servers that conflict with the provided public key ID.
    :rtype: list[Node]
    """
    repeaters: list[Node] = get_denver_repeaters()
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


def _find_unused_public_key_id_by_two_chars(nodes: list[Node]) -> str:
    """
    Find a public key ID in a list of nodes by comparing the first two characters (the first byte) of the public key.

    This is a temporary patch that will return XX00 for any public key, until MeshCore officially supports the full 4-character public key ID.
    """
    used_public_key_ids: set[str] = set(node.public_key_id_2_char for node in nodes)

    for i in range(256):
        public_key_id = f"{i:02x}"
        if is_reserved_public_key_id(public_key_id):
            continue
        if not _id_exists_in_list(id_=public_key_id, ids_to_track=list(used_public_key_ids)):
            return f"{public_key_id}00"

    raise RuntimeError("No available public key IDs found")


def _find_unused_public_key_id_by_four_chars(nodes: list[Node]) -> str:
    """
    Find a public key ID in a list of nodes by comparing the first four characters (the first two bytes) of the public key.
    This is the intended implementation once MeshCore officially supports the full 4-character public key ID.
    """
    used_public_key_ids: set[str] = set(node.public_key_id_4_char for node in nodes)

    for i in range(0x0000, 0x10000):
        public_key_id = f"{i:04x}"
        if is_reserved_public_key_id(public_key_id):
            continue
        if not _id_exists_in_list(id_=public_key_id, ids_to_track=list(used_public_key_ids)):
            return public_key_id

    raise RuntimeError("No available public key IDs found")


def suggest_public_key_id() -> str:
    """
    Suggest a new public key ID that is not currently in use.
    :return: A suggested public key ID that is not currently in use.
    :rtype: str
    """
    nodes: list[Node] = get_denver_nodes()

    # Iterate through all possible public key IDs and return the first one that is not in use
    return _find_unused_public_key_id_by_two_chars(nodes=nodes)
