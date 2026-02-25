import json

from flask import (
    Blueprint,
    render_template,
    request,
)

from backend.api.models.node_information import UserCompanionInformation, UserCompanionType
from backend.api.services.external_key_logic import suggest_public_key_id
from backend.api.services.name_generator import generate_companion_name
from backend.constants import (
    FLASK_GET,
    FLASK_POST
)
from backend.modules.emojis import EmojiTools

companion_name_tool = Blueprint("companion_name_tool", __name__, url_prefix="/companion_name_tool")

# Load recommended settings from static/data/recommended_settings.json file
with open('static/data/recommended_settings.json', 'r') as f:
    recommended_settings = json.load(f)

# Initialize emoji tools once at the module level to avoid reloading the emoji data on every request
emoji_tools = EmojiTools()


@companion_name_tool.route("/", methods=[FLASK_GET])
def index():
    role_types = [
        {'code': UserCompanionType.PRIMARY.value, "human_readable": UserCompanionType.PRIMARY.value,
         "description": "The primary companion device, the default method to contact a user."},
        {'code': UserCompanionType.SECONDARY.value, "human_readable": UserCompanionType.SECONDARY.value,
         "description": "A secondary companion device, less critical than the primary device but still used regularly"},
        {'code': UserCompanionType.TERTIARY.value, "human_readable": UserCompanionType.TERTIARY.value,
         "description": "A tertiary companion device, used occasionally or for a specific purpose."},
        {'code': UserCompanionType.BACKUP.value, "human_readable": UserCompanionType.BACKUP.value,
         "description": "A backup companion device, not regularly used. Serves as a fallback option if other devices are unavailable or not working."},
        {'code': UserCompanionType.EMERGENCY.value, "human_readable": UserCompanionType.EMERGENCY.value,
         "description": "An emergency companion device, reserved for critical situations. May have special configurations or settings to ensure it remains operational when other devices may not be."},
        {'code': UserCompanionType.MOBILE.value, "human_readable": UserCompanionType.MOBILE.value,
         "description": "A mobile companion device, designed to be portable and used on the go, such as hiking."},
        {'code': UserCompanionType.VEHICLE.value, "human_readable": UserCompanionType.VEHICLE.value,
         "description": "A vehicle companion device, intended for use in a car or other vehicle. May have features or configurations optimized for mobile use."},
        {'code': UserCompanionType.HOME.value, "human_readable": UserCompanionType.HOME.value,
         "description": "A home companion device, intended for use in a household or non-mobile setting. May have features or configurations optimized for home use."},
    ]
    return render_template('companion-name-tool.html',
                           role_types=role_types
                           )


# API endpoints
@companion_name_tool.route('/submit', methods=[FLASK_POST])
def generate_companion_details():
    """
    Generate companion name and public key ID recommendation given the details.
    return: A JSON object containing the generated companion details
    """
    data = request.get_json()
    node_information: UserCompanionInformation = UserCompanionInformation.model_validate(data,
                                                                                         context=dict(
                                                                                             emoji_tools=emoji_tools)
                                                                                         )

    suggested_public_key_id: str = suggest_public_key_id()

    name: str = generate_companion_name(
        emoji=node_information.emoji,
        handle=node_information.handle,
        public_key_id=suggested_public_key_id,
        role_type=node_information.role_type,
        role_counter=node_information.role_counter
    )

    import_json: dict = recommended_settings
    import_json['name'] = name

    return {
        "name": name,
        "public_key_id": suggested_public_key_id,
        "import_json": import_json,
        "import_json_file_name": f"denvermesh_meshcore_companion_config_{name}",
    }
