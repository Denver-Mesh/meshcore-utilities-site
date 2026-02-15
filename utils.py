import enum
from typing import Optional

NAMING_SCHEMA = "CO-{city}-{landmark}-{type}-{pub_key_id}"  # Ex. CO-DENVER-CHESSMN-RC-XX for a core repeater near Chessman Park in Denver, Colorado
NAMING_SCHEMA_ALT = "CO-{landmark}-{type}-{pub_key_id}"  # Ex. CO-PIKESPK-RC-XX for a core repeater on Pikes Peak, which is not within a city


class NodeType(enum.Enum):
    REPEATER_CORE = "Repeater - Core"
    REPEATER_DISTRIBUTOR = "Repeater - Distributor"
    REPEATER_EDGE = "Repeater - Edge"
    REPEATER_MOBILE = "Repeater - Mobile"
    ROOM_SERVER_STANDARD = "Room Server - Standard"
    ROOM_SERVER_REPEAT_ENABLED = "Room Server - Repeat Enabled"
    ROOM_SERVER_MOBILE = "Room Server - Mobile"
    COMPANION = "Companion"  # Should not be allowed for name generation, but included for completeness

    @classmethod
    def to_acronym(cls, node_type: 'NodeType') -> str:
        """
        Convert a NodeType to its corresponding acronym.
        :param node_type: The NodeType to convert.
        :type node_type: NodeType
        :return: The corresponding acronym (the first letter of the type).
        :rtype: str
        """
        if node_type == cls.REPEATER_CORE:
            return "RC"
        elif node_type == cls.REPEATER_DISTRIBUTOR:
            return "RD"
        elif node_type == cls.REPEATER_EDGE:
            return "RE"
        elif node_type == cls.REPEATER_MOBILE:
            return "RM"
        elif node_type == cls.ROOM_SERVER_STANDARD:
            return "T"
        elif node_type == cls.ROOM_SERVER_REPEAT_ENABLED:
            return "TR"
        elif node_type == cls.ROOM_SERVER_MOBILE:
            return "TM"
        else:
            raise ValueError(f"Unknown node type: {node_type}")


def public_key_to_public_key_id(public_key: str) -> str:
    """
    Convert a full public key to its corresponding public key ID (the first byte as a hex string).
    :param public_key: The full public key to convert.
    :type public_key: str
    :return: The corresponding public key ID (the first byte as a hex string).
    :rtype: str
    """
    return public_key[:2]


def is_reserved_public_key_id(public_key_id: str) -> bool:
    """
    Check if a public key ID is reserved.
    :param public_key_id: The public key ID to check.
    :type public_key_id: str
    :return: True if the public key ID is reserved, False otherwise.
    :rtype: bool
    """
    if public_key_id in ["00", "ff"]:
        return True

    return False


def generate_repeater_name(city: Optional[str],
                           landmark: str,
                           node_type: NodeType,
                           is_observer: bool,
                           public_key_id: str) -> str:
    """
    Generate a repeater name based on the provided details.
    :param city: The city code (up to 7 characters), optional since some locations may not be within a city.
    :type city: Optional[str]
    :param landmark: The landmark code (up to 7 characters if city is provided, up to 14 characters if city is not provided)
    :type landmark: str
    :param node_type: The type of node.
    :type node_type: NodeType
    :param is_observer: Whether the node is an observer
    :type is_observer: bool
    :param public_key_id: The public key ID (the first byte of the public key as a hex string).
    :type public_key_id: str
    :return: A generated repeater name based on the provided details.
    :rtype: str
    """
    # Ex. CO-DENVER-CHESSMN-RC-XX for a core repeater near Chessman Park in Denver, Colorado
    if node_type == NodeType.COMPANION:
        raise ValueError("Cannot generate names for companion nodes")

    suffix = NodeType.to_acronym(node_type=node_type)
    if is_observer:
        suffix += "+O"

    if not city:
        return NAMING_SCHEMA_ALT.format(
            landmark=landmark.upper(),
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )
    else:
        return NAMING_SCHEMA.format(
            city=city.upper(),
            landmark=landmark.upper(),
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )
