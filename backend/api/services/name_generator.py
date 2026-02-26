from typing import Optional

from backend.api.models.node_information import UserRepeaterType, UserCompanionType

# 3-5-5-2-4 = 19 + 4 = 23
REPEATER_NAMING_SCHEMA = "{region}-{city}-{landmark}-{type}-{pub_key_id}"  # Ex. DEN-DENVR-CHESSMN-RC-XXXX for a core repeater near Chessman Park in Denver, Colorado
# 3-11-2-4 = 20 + 3 = 23
REPEATER_NAMING_SCHEMA_ALT = "{region}-{landmark}-{type}-{pub_key_id}"  # Ex. COS-PIKESPEAK-RC-XXXX for a core repeater on Pikes Peak, which is not within a city

# 4 10 4 = 18 + 3 = 23
COMPANION_NAMING_SCHEMA_PKID = "{emoji}{handle} {public_key_id}"  # Ex. 🔥Alice XXXX for a companion device owned by Alice
# 4 10 4 = 18 + 3 = 23
COMPANION_NAMING_SCHEMA_COUNTER = "{emoji}{handle} MY{counter}"  # Ex. 🔥Alice MY01 for the primary companion device owned by Alice
# ^ M and Y are not a valid hex character, so it shouldn't be confused with a public key
# 4 10 4 = 18 + 3 = 23
COMPANION_NAMING_SCHEMA_ROLE = "{emoji}{handle} {role}"  # Ex. 🔥Alice PRIM for the primary companion device owned by Alice


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
    return public_key_id[:2].upper() in reserved_public_key_ids()


def reserved_public_key_ids() -> list[str]:
    """
    Get a list of all reserved public key IDs.
    :return: A list of all reserved public key IDs (2-character hex strings).
    :rtype: list[str]
    """
    reserved_ids = []

    # Add 00 and FF (reserved by LetsMesh/MeshMapper)
    reserved_ids.extend(["00", "FF"])

    # Add A-block (reserved by DenverMesh for future use), ref: https://ottawamesh.ca/deployment/repeaters-intercity/
    reserved_ids.extend([f"A{i:01X}" for i in range(16)])

    return reserved_ids


def generate_repeater_name(region: str,
                           city: Optional[str],
                           landmark: str,
                           node_type: UserRepeaterType,
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
    :type node_type: UserRepeaterType
    :param public_key_id: The public key ID (the first byte of the public key as a hex string).
    :type public_key_id: str
    :return: A generated repeater name based on the provided details.
    :rtype: str
    """
    # Ex. DEN-DENVR-CHESSMN-RC-XXXX for a core repeater near Chessman Park in Denver, Colorado
    # Ex. COS-PIKESPEAK-RC-XXXX for a core repeater on Pikes Peak, which is not within a city
    suffix = UserRepeaterType.to_acronym(node_type=node_type)

    if not city:
        return REPEATER_NAMING_SCHEMA_ALT.format(
            region=region.upper(),
            landmark=landmark,  # Not automatically uppercased
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )
    else:
        return REPEATER_NAMING_SCHEMA.format(
            region=region.upper(),
            city=city.upper(),
            landmark=landmark,  # Not automatically uppercased
            type=suffix.upper(),
            pub_key_id=public_key_id.upper()
        )


def generate_companion_name(handle: str,
                            public_key_id: str,
                            role_type: Optional[UserCompanionType] = None,
                            role_counter: Optional[int] = None,
                            emoji: Optional[str] = None) -> str:
    """
    Generate a companion name based on the provided details.
    :param handle: The handle or name of the companion device owner (e.g. "Alice").
    :param public_key_id: Public key ID to use as a fallback suffix if role_type and role_counter are not provided.
    :param role_type: Optional, a role type to use as a suffix.
    :param role_counter: Optional, a counter to denote importance of device.
    :param emoji: Optional, emoji to use as a prefix. If not provided, no emoji will be used.
    :return: A generated companion name based on the provided details.
    """
    # This should never happen because public_key_id is required
    if not any([public_key_id, role_type, role_counter]):
        raise ValueError("Either role_type, role_counter or public_key_id must be provided")

    emoji = emoji or ""  # Use empty string if emoji is None

    # Order of preference: role_type -> role_counter -> public_key_id
    if role_type:
        return COMPANION_NAMING_SCHEMA_ROLE.format(
            emoji=emoji,
            handle=handle,
            role=UserCompanionType.to_acronym(node_type=role_type)
        )
    elif role_counter:
        if not 1 <= role_counter <= 99:
            raise ValueError("role_counter must be between 1 and 99 inclusive")
        return COMPANION_NAMING_SCHEMA_COUNTER.format(
            emoji=emoji,
            handle=handle,
            counter=str(role_counter).zfill(2)  # Pad the counter with zeros to ensure it's always 2 digits
        )
    else:
        return COMPANION_NAMING_SCHEMA_PKID.format(
            emoji=emoji,
            handle=handle,
            public_key_id=public_key_id.upper()
        )
