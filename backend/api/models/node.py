from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from backend.api.models.node_status import NodeStatus
from backend.api.models.node_type import NodeType
from backend.modules import utils
from backend.modules.utils import timestamp_within_delta


class BaseNode(BaseModel, ABC):
    """
    An abstract base class representing a node, either from an API or used internally.
    """
    pass

    @abstractmethod
    def public_key_id(self) -> str:
        """
        Return the first byte (2-character hex string) of the public key, which is used as an identifier for the node.
        :return: The first byte of the public key as a hex string.
        :rtype: str
        """
        raise NotImplementedError("Subclasses must implement the public_key_id property")


class Node(BaseNode):
    """
    Internal representation of a generic node.
    Used for processing and comparing nodes from multiple API sources.
    """
    public_key: str
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    node_type: NodeType
    is_observer: bool = False
    contact: str | None
    created_at: int  # Unix timestamp
    last_heard: int  # Unix timestamp

    @property
    def public_key_id(self) -> str:
        """
        Return the first two bytes (4-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The first two bytes of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key_id_4_char

    @property
    def public_key_id_4_char(self) -> str:
        """
        Return the first two bytes (4-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The first two bytes of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key[:4].upper()

    @property
    def public_key_id_2_char(self) -> str:
        """
        Return the first byte (2-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The first byte of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key[:2].upper()

    @property
    def public_key_id_first_char(self) -> str:
        """
        Return the first character (1-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The first character of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key[0].upper()

    @property
    def public_key_id_second_char(self) -> str:
        """
        Return the second character (1-character hex string) of the public key, which is used as an identifier for the node.
        Always returns the public key ID in uppercase to ensure consistency when comparing with other nodes.
        :return: The second character of the public key as a hex string, in uppercase.
        :rtype: str
        """
        return self.public_key[1].upper()

    @property
    def hash(self) -> int:
        """
        Generate a hash value for this node
        :return: An integer hash value representing this node.
        """
        _input = f"{self.name}:{self.public_key_id}:{self.node_type.value}:{self.latitude}:{self.longitude}:{self.is_observer}"
        return hash(_input)

    @property
    def status(self) -> NodeStatus:
        """
        Determine the status of this node based on its created_at and last_heard timestamps.
        :return: A NodeStatus value representing the status of this node.
        """
        if not self.last_heard:  # Not sure when last heard, so we can't determine status
            return NodeStatus.UNKNOWN
        elif timestamp_within_delta(timestamp=self.created_at, days=2):  # First heard within the last 2 days
            return NodeStatus.NEW
        elif timestamp_within_delta(timestamp=self.last_heard, days=7):  # Last heard within the last 7 days
            return NodeStatus.ACTIVE
        else:  # Last heard was more than 7 days ago
            return NodeStatus.STALE

    def to_json(self) -> dict:
        """
        Serialize this node to a JSON-compatible dictionary
        :return: A dictionary representation of this node that can be serialized to JSON.
        """
        return {
            'public_key': self.public_key,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'node_type': self.node_type.value,
            'is_observer': self.is_observer,
            'contact': self.contact,
            'created_at': self.created_at,
            'last_heard': self.last_heard,
        }
