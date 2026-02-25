from typing import Optional

from pydantic import BaseModel, model_validator, Field, field_validator

from backend.utils import NodeType


class NodeInformation(BaseModel):
    region: Optional[str] = Field(alias="region")  # Required regional code
    city: Optional[str] = Field(alias="city",
                                default=None)  # <=5-char city code, optional since some locations may not be within a city
    landmark: str = Field(alias="landmark", default=None)  # <=5-char landmark code
    node_type: NodeType = Field(alias="node-type")

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
