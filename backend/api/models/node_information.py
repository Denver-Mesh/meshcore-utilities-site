import enum
from typing import Optional, Any

from pydantic import BaseModel, model_validator, Field, field_validator, ValidationInfo

from backend.modules.emojis import EmojiTools


class UserRepeaterType(enum.Enum):
    REPEATER_CORE = "Repeater - Core"
    REPEATER_DISTRIBUTOR = "Repeater - Distributor"
    REPEATER_EDGE = "Repeater - Edge"
    REPEATER_MOBILE = "Repeater - Mobile"
    ROOM_SERVER_STANDARD = "Room Server - Standard"
    ROOM_SERVER_MOBILE = "Room Server - Mobile"
    ROOM_SERVER_REPEAT_ENABLED = "Room Server - Repeat Enabled"

    @classmethod
    def to_acronym(cls, node_type: 'UserRepeaterType') -> str:
        """
        Convert a UserRepeaterType to its corresponding acronym.
        :param node_type: The UserRepeaterType to convert.
        :type node_type: UserRepeaterType
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


class UserRepeaterInformation(BaseModel):
    region: Optional[str] = Field(alias="region")  # Required regional code
    city: Optional[str] = Field(alias="city",
                                default=None)  # <=5-char city code, optional since some locations may not be within a city
    landmark: str = Field(alias="landmark", default=None)  # <=5-char landmark code
    node_type: UserRepeaterType = Field(alias="node-type")

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


class UserCompanionType(enum.Enum):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    TERTIARY = "Tertiary"
    BACKUP = "Backup"
    EMERGENCY = "Emergency"
    MOBILE = "Mobile"
    VEHICLE = "Vehicle"
    HOME = "Home"

    @classmethod
    def to_acronym(cls, node_type: 'UserCompanionType') -> str:
        """
        Convert a UserCompanionType to its corresponding acronym.
        :param node_type: The UserCompanionType to convert.
        :type node_type: UserCompanionType
        :return: The corresponding acronym (<=4 characters)
        :rtype: str
        """
        if node_type == cls.PRIMARY:
            return "PRIM"
        elif node_type == cls.SECONDARY:
            return "SEC"
        elif node_type == cls.TERTIARY:
            return "TERT"
        elif node_type == cls.BACKUP:
            return "BACK"
        elif node_type == cls.EMERGENCY:
            return "EMER"
        elif node_type == cls.HOME:
            return "HOME"
        elif node_type == cls.MOBILE:
            return "MOB"
        elif node_type == cls.VEHICLE:
            return "VEH"
        else:
            raise ValueError(f"Unknown node type: {node_type}")


class UserCompanionInformation(BaseModel):
    handle: str = Field(alias="handle")  # The handle or name of the companion device owner (e.g. "Alice")
    emoji: Optional[str] = Field(alias="emoji", default=None)  # Optional emoji prefix for companion names
    role_type: Optional[UserCompanionType] = Field(alias="role-type", default=None)  # Optional role type
    role_counter: Optional[int] = Field(alias="suffix-number", default=None)  # Optional counter to denote importance of device

    @field_validator('role_counter', mode='before')
    @classmethod
    def validate_role_counter(cls, value: Any) -> Any:
        if isinstance(value, str) and not value:  # Replace string with None if it's an empty string
            return None

        return value

    @model_validator(mode="after")
    def validate_model(self, info: ValidationInfo):
        context = info.context if isinstance(info.context, dict) else {}

        # With (optional) 4-char emoji and <=4-char suffix, plus spaces, handle must be <=10 chars for 23 char limit
        if len(self.handle) > 10:
            raise ValueError("Handle must be up to 10 characters long")

        if self.emoji:
            emoji_tools: EmojiTools = context.get('emoji_tools', None)
            if emoji_tools and not emoji_tools.validate_emoji_unicode(self.emoji):
                raise ValueError("Invalid emoji provided")

        if self.role_counter and not (1 <= self.role_counter <= 99):
            raise ValueError("Role counter must be between 1 and 99")

        return self
