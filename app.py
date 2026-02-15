import os
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, render_template, request
from pydantic import BaseModel, model_validator, Field, field_validator

import letsmesh
import utils
from database import Database, save_node_to_database, get_nodes_matching_partial_name
from utils import NodeType

app = Flask(__name__)
app.config['DATABASE_URL'] = f'sqlite:///{os.environ.get("DATABASE_FILE")}'


def _database_call(func, *args, **kwargs):
    """
    Helper function to wrap database calls in a try-except block
    :param func: The database function to call
    :param args: Positional arguments to pass to the database function
    :param kwargs: Keyword arguments to pass to the database function
    :return: The result of the database function, or None if an error occurred
    """
    try:
        database = Database(url=app.config['DATABASE_URL'])
        return func(database, *args, **kwargs)
    except Exception as e:
        print(f'Error calling database function {func.__name__}: {e}')
        return None


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
    cities = [
        {'code': '', 'name': '---'},
        {'code': 'DENVER', 'name': 'Denver'},
        {'code': 'AURORA', 'name': 'Aurora'},
        {'code': 'LKWD', 'name': 'Lakewood'},
        {'code': 'ARVADA', 'name': 'Arvada'},
        {'code': 'WSTMNR', 'name': 'Westminster'},
        {'code': 'THRTON', 'name': 'Thornton'},
        {'code': 'CENTL', 'name': 'Centennial'},
        {'code': 'BROOM', 'name': 'Broomfield'},
        {'code': 'LTTN', 'name': 'Littleton'},
        {'code': 'ENGL', 'name': 'Englewood'},
        {'code': 'CMRCE', 'name': 'Commerce City'},
        {'code': 'GLDN', 'name': 'Golden'},
        {'code': 'BOULDR', 'name': 'Boulder'},
        {'code': 'PARKER', 'name': 'Parker'},
        {'code': 'CSTLRK', 'name': 'Castle Rock'},
        {'code': 'HGHLND', 'name': 'Highlands Ranch'},
        {'code': 'CSPRGS', 'name': 'Colorado Springs'},
        {'code': 'LSVL', 'name': 'Louisville'},
        {'code': 'LFAYTE', 'name': 'Lafayette'},
    ]
    return render_template('index.html',
                           # Sort city options alphabetically by name, but keep the blank option at the top
                           cities=sorted(cities, key=lambda x: (x['code'] != '', x['name'])),
                           node_types=[_type.value for _type in NodeType])


# API endpoints
@app.route('/api/generate_repeater_details', methods=['POST'])
def generate_repeater_details():
    """
    Generate repeater name and public key ID recommendation given the details.
    return: A JSON object containing the generated repeater details
    """
    # Incoming request is form-data, so we need to convert it to JSON before parsing it with Pydantic
    data = request.values
    node_information: NodeInformation = NodeInformation(**data)

    suggested_public_key_id: str = letsmesh.suggest_public_key_id()

    name: str = utils.generate_repeater_name(
        city=node_information.city,
        landmark=node_information.landmark,
        node_type=node_information.node_type,
        is_observer=node_information.is_observer,
        public_key_id=suggested_public_key_id,
    )

    return render_template("repeater_details.html", name=name, public_key_id=suggested_public_key_id)


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


@app.route('/api/submit_node', methods=['POST'])
def submit_node():
    """
    Submit a node to be added to the database
    :return: A JSON object containing a boolean indicating whether the node was successfully added to the database
    """
    data = request.get_json()
    public_key: str = data.get('public_key')
    name: str = data.get('name')

    try:
        _database_call(func=save_node_to_database, public_key=public_key, name=name)
        success = True
    except Exception as e:
        print(f'Error submitting node: {e}')
        success = False

    return {
        "success": success,
    }


if __name__ == '__main__':
    load_dotenv()
    app.run(debug=True, host='0.0.0.0', port=50000)
