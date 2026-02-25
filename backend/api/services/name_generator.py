from typing import Optional

from backend.api.models.node_information import UserNodeType

# 3-5-5-2-4 or 3-11-2-4
NAMING_SCHEMA = "{region}-{city}-{landmark}-{type}-{pub_key_id}"  # Ex. DEN-DENVR-CHESSMN-RC-XXXX for a core repeater near Chessman Park in Denver, Colorado
NAMING_SCHEMA_ALT = "{region}-{landmark}-{type}-{pub_key_id}"  # Ex. COS-PIKESPEAK-RC-XXXX for a core repeater on Pikes Peak, which is not within a city


def public_key_to_public_key_id(public_key: str) -> str:
    """
    Convert a full public key to its corresponding public key ID (the first two bytes as a hex string).
    :param public_key: The full public key to convert.
    :type public_key: str
    :return: The corresponding public key ID (the first byte as a hex string).
    :rtype: str
    """
    return public_key[:4]


def is_reserved_public_key_id(public_key_id: str) -> bool:
    """
    Check if a public key ID is reserved.
    :param public_key_id: The public key ID to check (2 or 4 hex characters).
    :type public_key_id: str
    :return: True if the public key ID is reserved, False otherwise.
    :rtype: bool
    """
    if public_key_id[:2].upper() in ["00", "FF"]:  # Reserved by LetsMesh/MeshMapper
        return True

    # ref: https://ottawamesh.ca/deployment/repeaters-intercity/
    if public_key_id[:1].upper() in ['A']:  # A-block reserved by DenverMesh for future use
        return True

    return False


def generate_repeater_name(region: str,
                           city: Optional[str],
                           landmark: str,
                           node_type: UserNodeType,
                           public_key_id: str) -> str:
    """
    Generate a repeater name based on the provided details.
    :param region: The region code (up to 3 characters), required since all locations should be within a defined region.
    :type region: str
    :param city: The city code (up to 5 characters), optional since some locations may not be within a city.
    :type city: Optional[str]
    :param landmark: The landmark code (up to 5 characters if city is provided, up to 11 characters if city is not provided)
    :type landmark: str
    :param node_type: The type of node.
    :type node_type: UserNodeType
    :param public_key_id: The public key ID (the first byte of the public key as a hex string).
    :type public_key_id: str
    :return: A generated repeater name based on the provided details.
    :rtype: str
    """
    # Ex. DEN-DENVR-CHESSMN-RC-XXXX for a core repeater near Chessman Park in Denver, Colorado
    # Ex. COS-PIKESPEAK-RC-XXXX for a core repeater on Pikes Peak, which is not within a city
    if node_type == UserNodeType.COMPANION:
        raise ValueError("Cannot generate names for companion nodes")

    suffix = UserNodeType.to_acronym(node_type=node_type)

    if not city:
        return NAMING_SCHEMA_ALT.format(
            region=region.upper(),
            landmark=landmark,  # Not automatically uppercased
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )
    else:
        return NAMING_SCHEMA.format(
            region=region.upper(),
            city=city.upper(),
            landmark=landmark,  # Not automatically uppercased
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )
