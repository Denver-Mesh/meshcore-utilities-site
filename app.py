import json
from typing import Optional

from flask import Flask, render_template, request
from pydantic import BaseModel, model_validator, Field, field_validator

import letsmesh
import utils
from utils import NodeType

app = Flask(__name__)

# Load cities from static/data/cities.json file
with open('static/data/cities.json', 'r') as f:
    cities = json.load(f)

# Load recommended settings from static/data/recommended_settings.json file
with open('static/data/recommended_settings.json', 'r') as f:
    recommended_settings = json.load(f)


class NodeInformation(BaseModel):
    city: Optional[str] = Field(alias="city",
                                default=None)  # <=7-char city code, optional since some locations may not be within a city
    landmark: str = Field(alias="landmark", default=None)  # <=7-char landmark code
    node_type: NodeType = Field(alias="node-type")
    is_observer: bool = Field(alias="is-observer", default=False)

    @classmethod
    @field_validator('is_observer', mode='before')
    def validate_is_observer(cls, value):
        if isinstance(value, str):
            value = value.lower() in ['true', '1', 'yes', 'on']
        return value

    @model_validator(mode="after")
    def validate_model(self):
        # Need either <=7 city and <=7 landmark, or a <=14 landmark
        if self.city:
            if len(self.city) > 7:
                raise ValueError("City code must be up to 7 characters long")
            if len(self.landmark) > 7:
                raise ValueError("Landmark code must be up to 7 characters long")
        elif len(self.landmark) > 14:
            raise ValueError("Landmark code must be up to 14 characters long if city code is not provided")

        return self


# Serve the main HTML page
@app.route('/')
def index():
    node_types = [
        {'code': NodeType.REPEATER_CORE.value, 'human_readable': NodeType.REPEATER_CORE.value,
         'description': 'A repeater that serves as a critical backbone for the mesh network. Should be permanently installed in a fixed, high-elevation location. Typically solar-powered.'},
        {'code': NodeType.REPEATER_DISTRIBUTOR.value, 'human_readable': NodeType.REPEATER_DISTRIBUTOR.value,
         'description': 'A repeater that serves as a bridge between core repeaters and edge repeaters. Should be placed in a fixed, elevated suburban location. Typically solar-powered.'},
        {'code': NodeType.REPEATER_EDGE.value, 'human_readable': NodeType.REPEATER_EDGE.value,
         'description': 'A repeater that connects a neighborhood or building to distributor or core repeaters. Should be installed on residential rooftops or near windows. Can be solar-powered or plugged in, depending on location and power availability.'},
        {'code': NodeType.REPEATER_MOBILE.value, 'human_readable': NodeType.REPEATER_MOBILE.value,
         'description': 'A repeater that is temporarily installed and can be moved to different locations as needed, or is installed in a vehicle.'},
        {'code': NodeType.ROOM_SERVER_STANDARD.value, 'human_readable': NodeType.ROOM_SERVER_STANDARD.value,
         'description': 'A room server that is permanently installed at a fixed location.'},
        {'code': NodeType.ROOM_SERVER_MOBILE.value, 'human_readable': NodeType.ROOM_SERVER_MOBILE.value,
         'description': 'A room server that is temporarily installed and can be moved to different locations as needed, or is installed in a vehicle.'},
        {'code': NodeType.ROOM_SERVER_REPEAT_ENABLED.value, 'human_readable': NodeType.ROOM_SERVER_REPEAT_ENABLED.value,
         'description': 'A room server with repeater capabilities enabled. NOTE: While room servers can have repeater capabilities enabled, it is not officially recommended.'},

    ]
    return render_template('index.html',
                           # Sort city options alphabetically by name, but keep the blank option at the top
                           cities=sorted(cities, key=lambda x: (x['code'] != '', x['name'])),
                           node_types=node_types)


# API endpoints
@app.route('/api/generate_repeater_details', methods=['POST'])
def generate_repeater_details():
    """
    Generate repeater name and public key ID recommendation given the details.
    return: A JSON object containing the generated repeater details
    """
    data = request.get_json()
    node_information: NodeInformation = NodeInformation(**data)

    suggested_public_key_id: str = letsmesh.suggest_public_key_id()

    name: str = utils.generate_repeater_name(
        city=node_information.city,
        landmark=node_information.landmark,
        node_type=node_information.node_type,
        is_observer=node_information.is_observer,
        public_key_id=suggested_public_key_id,
    )

    import_json: dict = recommended_settings
    import_json['name'] = name

    return {
        "name": name,
        "public_key_id": suggested_public_key_id,
        "import_json": import_json,
        "import_json_file_name": f"denvermesh_meshcore_starter_config_{name}",
    }


# API endpoints
@app.route('/api/validate_public_key', methods=['POST'])
def validate_public_key():
    """
    Validate a public key
    :return: A JSON object containing a boolean indicating whether the public key is valid
    """
    data = request.get_json()
    public_key: str = data.get('public_key')
    public_key_id: str = utils.public_key_to_public_key_id(public_key=public_key)

    valid = (
            len(letsmesh.get_conflicting_nodes(public_key_id=public_key_id)) <= 0 and
            not letsmesh.is_reserved_public_key_id(public_key_id=public_key_id)
    )

    return {
        "valid": valid,
    }


@app.route('/api/suggest_public_key_id', methods=['GET'])
def suggest_public_key_id():
    """
    Suggest a public key ID that does not conflict with any existing nodes in the Denver region.
    :return: A JSON object containing a suggested public key ID
    """
    suggested_public_key_id: str = letsmesh.suggest_public_key_id()
    return {
        "public_key_id": suggested_public_key_id,
    }


if __name__ == '__main__':
    # In Docker, we want to bind to all interfaces and disable debug mode
    app.run(debug=False, host='0.0.0.0', port=50000)
