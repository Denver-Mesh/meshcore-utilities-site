import json

from flask import (
    Blueprint,
    render_template,
    request,
)

from backend.api.models.node_information import NodeInformation, UserNodeType
from backend.api.services.external_key_logic import suggest_public_key_id
from backend.api.services.name_generator import generate_repeater_name
from backend.constants import (
    FLASK_GET,
)

name_tool = Blueprint("name_tool", __name__, url_prefix="/name_tool")

# Load cities from static/data/regions.json file
with open('static/data/regions.json', 'r') as f:
    regions = json.load(f)

# Sort airport options alphabetically by name
airport_codes = []
for airport in sorted(regions['airports'], key=lambda x: x['name']):
    airport_codes.append({"name": airport['name'], "code": airport['code']})

# Sort city options alphabetically by name, with blank option at the top
cities_five_char_limit = [
    {"name": "---", "code": ""}
]
for city in sorted(regions['cities'], key=lambda x: x['name']):
    cities_five_char_limit.append({"name": city['name'], "code": city['codes']['five']})

# Load recommended settings from static/data/recommended_settings.json file
with open('static/data/recommended_settings.json', 'r') as f:
    recommended_settings = json.load(f)


@name_tool.route("/", methods=[FLASK_GET])
def index():
    node_types = [
        {'code': UserNodeType.REPEATER_EDGE.value, 'human_readable': UserNodeType.REPEATER_EDGE.value,
         'description': 'A repeater that connects a neighborhood or building to distributor or core repeaters. Should be installed on residential rooftops or near windows. Can be solar-powered or plugged in, depending on location and power availability.'},
        {'code': UserNodeType.REPEATER_DISTRIBUTOR.value, 'human_readable': UserNodeType.REPEATER_DISTRIBUTOR.value,
         'description': 'A repeater that serves as a bridge between core repeaters and edge repeaters. Should be placed in a fixed, elevated suburban location. Typically solar-powered.'},
        {'code': UserNodeType.REPEATER_CORE.value, 'human_readable': UserNodeType.REPEATER_CORE.value,
         'description': 'A repeater that serves as a critical backbone for the mesh network. Should be permanently installed in a fixed, high-elevation location. Typically solar-powered. Please coordinate with community members before installing a core repeater.'},
        {'code': UserNodeType.REPEATER_MOBILE.value, 'human_readable': UserNodeType.REPEATER_MOBILE.value,
         'description': 'A repeater that is temporarily installed and can be moved to different locations as needed, or is installed in a vehicle.'},
        {'code': UserNodeType.ROOM_SERVER_STANDARD.value, 'human_readable': UserNodeType.ROOM_SERVER_STANDARD.value,
         'description': 'A room server that is permanently installed at a fixed location.'},
        {'code': UserNodeType.ROOM_SERVER_MOBILE.value, 'human_readable': UserNodeType.ROOM_SERVER_MOBILE.value,
         'description': 'A room server that is temporarily installed and can be moved to different locations as needed, or is installed in a vehicle.'},
        {'code': UserNodeType.ROOM_SERVER_REPEAT_ENABLED.value,
         'human_readable': UserNodeType.ROOM_SERVER_REPEAT_ENABLED.value,
         'description': 'A room server with repeater capabilities enabled. NOTE: While room servers can have repeater capabilities enabled, it is not officially recommended.'},

    ]
    return render_template('name-tool.html',
                           regions=airport_codes,
                           cities=cities_five_char_limit,
                           node_types=node_types)


# API endpoints
@name_tool.route('/submit', methods=['POST'])
def generate_repeater_details():
    """
    Generate repeater name and public key ID recommendation given the details.
    return: A JSON object containing the generated repeater details
    """
    data = request.get_json()
    node_information: NodeInformation = NodeInformation(**data)

    suggested_public_key_id: str = suggest_public_key_id()

    name: str = generate_repeater_name(
        region=node_information.region,
        city=node_information.city,
        landmark=node_information.landmark,
        node_type=node_information.node_type,
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
