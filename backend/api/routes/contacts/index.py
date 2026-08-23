import json
from typing import Optional

from coloradomesh.meshcore.models.general import Regions
from coloradomesh.meshcore.services.contacts import ContactsOrder, ContactsStatus, ContactsType, prepare_contacts
from flask import (
    Blueprint,
    render_template,
    request,
)

from backend.constants import (
    FLASK_GET, 
    FLASK_POST,
)

contacts = Blueprint("contacts", __name__, url_prefix="/contacts")

@contacts.route("/", methods=[FLASK_GET], strict_slashes=False)
def index():
    status_filter = [
        {'code': ContactsStatus.ALL.value, "human_readable": 'All',
         'description': 'All nodes.'},
        {'code': ContactsStatus.ACTIVE.value, "human_readable": 'Active only',
         'description': 'Only nodes that are active.'},
    ]
    
    order_filter = [
        {'code': ContactsOrder.RECENT.value, "human_readable": 'Recently heard',
         'description': 'Sort by most recently heard first.'},
        {'code': ContactsOrder.NEWEST.value, "human_readable": 'Newest',
         'description': 'Sort by newest nodes first.'},
        {'code': ContactsOrder.OLDEST.value, "human_readable": 'Oldest',
         'description': 'Sort by oldest nodes first.'},
        {'code': ContactsOrder.ALPHABETICAL.value, "human_readable": 'Alphabetical (Name)',
         'description': 'Sort alphabetically by name.'},
        {'code': ContactsOrder.IDENTITY.value, "human_readable": 'Alphabetical (Public ID)',
         'description': 'Sort alphabetically by public ID.'},
    ]
    
    type_filter = [
        {'code': ContactsType.ALL.value, "human_readable": 'All',
         'description': 'All types of nodes'},
        {'code': ContactsType.COMPANIONS.value, "human_readable": 'Only Companions (Users)',
         'description': 'Only companions.'},
        {'code': ContactsType.REPEATERS.value, "human_readable": 'Only Repeaters',
         'description': 'Only repeaters.'},
        {'code': ContactsType.ROOMS.value, "human_readable": 'Only Rooms',
         'description': 'Only repeaters.'},
        {'code': ContactsType.REPEATERS_AND_ROOMS.value, "human_readable": 'Only Repeaters and Rooms',
         'description': 'Only repeaters and rooms.'},
    ]
    region_filter = [
        {'code': "none", "human_readable": "All",
         'description': 'All regions'}
    ]
    region_filter.extend([
        {'code': region.value.code, "human_readable": f"{region.value.code.upper()} - {region.value.name}",
         'description': f'Only nodes near {region.value.name}'}
        for region in Regions
    ])
    
    return render_template('contacts.html',
                           status_filter=status_filter,
                           order_filter=order_filter,
                           type_filter=type_filter,
                           region_filter=region_filter,
                           )


# API endpoints
@contacts.route('/download', methods=[FLASK_POST])
def download_contacts():
    """
    Send a JSON file with contacts in Colorado.
    return: A JSON object with a list of contacts in Colorado.
    """
    # Check if an "id" query parameter is provided
    args = request.get_json()
    _limit: int = args.get('limit', 250)  # Default to 250 limit (can't hold infinite contacts in MeshCore app)
    _order: Optional[ContactsOrder] = args.get("order", None)
    _status: Optional[ContactsStatus] = args.get("status", None)
    _type: Optional[ContactsType] = args.get("type", None)
    _region: Optional[str] = args.get("region", None)
    
    if _region == 'none':
        _region = None

    data = prepare_contacts(count=_limit, order=_order, status=_status, _type=_type, region_iata=_region)
    return json.dumps(data)