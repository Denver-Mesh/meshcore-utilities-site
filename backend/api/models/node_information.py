import enum
from typing import Optional

from pydantic import BaseModel, model_validator, Field, field_validator


class UserNodeType(enum.Enum):
    REPEATER_CORE = "Repeater - Core"
    REPEATER_DISTRIBUTOR = "Repeater - Distributor"
    REPEATER_EDGE = "Repeater - Edge"
    REPEATER_MOBILE = "Repeater - Mobile"
    ROOM_SERVER_STANDARD = "Room Server - Standard"
    ROOM_SERVER_MOBILE = "Room Server - Mobile"
    ROOM_SERVER_REPEAT_ENABLED = "Room Server - Repeat Enabled"
    COMPANION = "Companion"  # Should not be allowed for name generation, but included for completeness

    @classmethod
    def to_acronym(cls, node_type: 'UserNodeType') -> str:
        """
        Convert a UserNodeType to its corresponding acronym.
        :param node_type: The UserNodeType to convert.
        :type node_type: UserNodeType
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
            return "TS"
        elif node_type == cls.ROOM_SERVER_REPEAT_ENABLED:
            return "TR"
        elif node_type == cls.ROOM_SERVER_MOBILE:
            return "TM"
        else:
            raise ValueError(f"Unknown node type: {node_type}")


class NodeInformation(BaseModel):
    region: Optional[str] = Field(alias="region")  # Required regional code
    city: Optional[str] = Field(alias="city",
                                default=None)  # <=5-char city code, optional since some locations may not be within a city
    landmark: str = Field(alias="landmark", default=None)  # <=5-char landmark code
    node_type: UserNodeType = Field(alias="node-type")

    @classmethod
    @field_validator('is_observer', mode='before')
    def validate_is_observer(cls, value):
        if isinstance(value, str):
            value = value.lower() in ['true', '1', 'yes', 'on']
        return value

    @model_validator(mode="after")
    def validate_model(self):
        # Need either <=5 city and <=5 landmark, or a <=11 landmark
        if self.city:
            if len(self.city) > 5:
                raise ValueError("City code must be up to 5 characters long")
            if len(self.landmark) > 5:
                raise ValueError("Landmark code must be up to 5 characters long")
        elif len(self.landmark) > 11:
            raise ValueError("Landmark code must be up to 11 characters long if city code is not provided")

        return self
