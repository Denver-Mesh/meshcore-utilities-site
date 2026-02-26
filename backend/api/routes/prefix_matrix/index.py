import json
from collections import Counter

from flask import (
    Blueprint,
    render_template,
)

from backend.api.models.node import Node
from backend.api.models.node_status import NodeStatus
from backend.api.services.external_key_logic import get_denver_repeaters
from backend.api.services.name_generator import is_reserved_public_key_id, reserved_public_key_ids
from backend.constants import (
    FLASK_GET,
)
from backend.modules.utils import epoch_to_datetime

prefix_matrix = Blueprint("prefix_matrix", __name__, url_prefix="/prefix_matrix")

# All reserved IDs (2-char hex strings)
reserved_ids = reserved_public_key_ids()

# All possible (2-char) IDs (not reserved)
# This is slow as it's O(n^2) loop with the is_reserved_public_key_id check, so we do it once here (as long as reservations don't change often)
possible_ids: list[str] = [f"{i:02X}" for i in range(256) if not is_reserved_public_key_id(public_key_id=f"{i:02X}")]

def _build_repeater_info(repeater: Node) -> dict:
    return {
        "status": repeater.status.to_str(),
        "status_value": repeater.status.to_str().upper(),
        "location": f"{repeater.latitude}, {repeater.longitude}" if all([repeater.latitude, repeater.longitude]) else "N/A",
        "last_heard": epoch_to_datetime(repeater.last_heard),
        "id": repeater.public_key_id_2_char,
        "public_key": repeater.public_key,
        "name": repeater.name,
        "contact_url": repeater.contact,
    }

def _build_info_json(repeaters: list[Node]) -> str:
    if len(repeaters) == 1:
        return json.dumps(_build_repeater_info(repeaters[0]))
    else:
        return json.dumps([_build_repeater_info(repeater) for repeater in repeaters])

def _build_matrix_entry(cell_id: str, repeaters: list[Node]) -> dict:
    # repeaters may be empty (free), have one entry (used), or multiple entries (duplicate)
    if not repeaters:
        css_class = "hex-free"
        if cell_id in reserved_ids:
            css_class += " hex-reserved"
        on_click_action = ""
    elif len(repeaters) == 1:
        css_class = "hex-used"
        info_json = _build_info_json(repeaters)
        on_click_action = f'showRepeaterInfo("{cell_id}", {info_json})'
    else:  # len(repeaters) > 1
        css_class = "hex-duplicate"
        info_json = _build_info_json(repeaters)
        on_click_action = f'showDuplicateInfo("{cell_id}", {info_json})'

    if not any(repeater.status == NodeStatus.ACTIVE for repeater in repeaters):
        css_class += " hex-inactive"

    return {
        "id": cell_id,
        "css_class": css_class,
        "onclick_js_action": on_click_action,
    }


def _build_matrix_row(row_hex_char: str, repeaters: list[Node]) -> dict:
    row_cells = {}

    for col_hex_char in _hex_chars():
        cell_id = f"{row_hex_char}{col_hex_char}"
        repeaters_with_cell_id = [repeater for repeater in repeaters if repeater.public_key_id_2_char == cell_id]
        row_cells[col_hex_char] = _build_matrix_entry(cell_id=cell_id, repeaters=repeaters_with_cell_id)

    """
    {
        "cells": {
            "0": {
                "repeaters": [...],
                "css_class": "hex-duplicate"
                ...
            },
            ...
        },
        "extra": "data here"
    }
    """
    return {
        "cells": row_cells
    }


def _build_matrix(repeaters: list[Node]) -> dict[str, dict]:
    matrix = {}

    for row_hex_char in _hex_chars():
        repeaters_starting_with_hex_char = [repeater for repeater in repeaters if
                                            repeater.public_key_id_first_char == row_hex_char]
        matrix[row_hex_char] = _build_matrix_row(row_hex_char=row_hex_char, repeaters=repeaters_starting_with_hex_char)

    """
    {
      "0": {
        "cells": {
            "0": {
                "repeaters": [],
                "css_class": "hex-free"
            }
            ...
        },
        "extra": "data here"
      }
      ...
    }
    """

    return matrix


def _hex_chars() -> list[str]:
    return [f"{i:X}".upper() for i in range(16)]


@prefix_matrix.route("/", methods=[FLASK_GET])
def index():
    repeaters: list[Node] = get_denver_repeaters()

    # Count occurrences of each (2-char) ID
    id_list = [repeater.public_key_id_2_char for repeater in repeaters]
    id_counts = Counter(id_list)

    # Find duplicates
    ids_with_duplicates = {id_val for id_val, count in id_counts.items() if count > 1}

    # Used IDs (all repeater IDs)
    used_ids = set(id_list)

    # Create a lookup dictionary for repeater info by ID
    repeater_info = {}

    for repeater in repeaters:
        repeater_id = repeater.public_key_id_2_char

        if repeater_id not in repeater_info.keys():
            repeater_info[repeater_id] = []

        repeater_info[repeater_id].append(repeater)

    # All unused possible IDs (not in used_ids and not reserved)
    available_ids: list[str] = [id_val for id_val in possible_ids if id_val not in used_ids]
    available_ids.sort(key=lambda x: int(x, 16))  # Sort in hex order

    matrix_data: dict = _build_matrix(repeaters)

    return render_template('prefix_matrix.html',
                           matrix_data=matrix_data,
                           hex_chars=_hex_chars(),
                           )
