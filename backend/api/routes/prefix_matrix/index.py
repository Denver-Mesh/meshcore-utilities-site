import json

from coloradomesh.internal.utils import epoch_to_datetime  # Probably shouldn't be accessing internal utils
from coloradomesh.meshcore.models.general import Node
from coloradomesh.meshcore.models.general import NodeStatus
from coloradomesh.meshcore.services.public_keys import reserved_public_key_ids
from flask import (
    Blueprint,
    render_template,
)

from backend.api.services.external_key_logic import get_denver_repeaters
from backend.constants import (
    FLASK_GET,
)

prefix_matrix = Blueprint("prefix_matrix", __name__, url_prefix="/prefix_matrix")

# Normalize once for consistent comparisons
reserved_ids = {rid.upper() for rid in reserved_public_key_ids()}


def _hex_chars() -> list[str]:
    return [f"{i:X}".upper() for i in range(16)]


def _build_repeater_info(repeater: Node) -> dict:
    rid = _get_4char_id(repeater)
    return {
        "status": repeater.status.to_str(),
        "status_value": repeater.status.to_str().upper(),
        "location": f"{repeater.latitude}, {repeater.longitude}" if all(
            [repeater.latitude, repeater.longitude]) else "N/A",
        "last_heard": epoch_to_datetime(repeater.last_heard),
        "id": rid,
        "is_reserved_id": _is_reserved_id(rid),
        "public_key": repeater.public_key,
        "name": repeater.name,
        "contact_url": repeater.contact_url,
    }


def _build_info_json(repeaters: list[Node]) -> str:
    if len(repeaters) == 1:
        return json.dumps(_build_repeater_info(repeaters[0]))
    else:
        return json.dumps([_build_repeater_info(repeater) for repeater in repeaters])


def _build_search_infos(repeaters: list[Node]) -> list[dict]:
    return [_build_repeater_info(repeater) for repeater in repeaters]


def _build_search_text(repeaters: list[Node]) -> str:
    searchable_values = []
    for info in _build_search_infos(repeaters):
        searchable_values.extend([
            info.get("id"),
            info.get("name"),
            info.get("location"),
            info.get("status"),
            info.get("status_value"),
            info.get("public_key"),
            info.get("contact_url"),
            info.get("last_heard"),
        ])
    return " ".join(str(value) for value in searchable_values if value).lower()


def _get_4char_id(repeater: Node) -> str:
    """Get the first 4 hex chars of a node's public key ID."""
    return getattr(repeater, 'public_key_id_4_char', repeater.public_key_id_2_char).upper()


def _is_reserved_id(cell_id_4: str) -> bool:
    cell_id_4 = cell_id_4.upper()
    return cell_id_4 in reserved_ids or cell_id_4[:2] in reserved_ids


def _build_sub_cell(cell_id_4: str, repeaters: list[Node]) -> dict:
    """Build a single cell for the secondary (chars 3&4) grid."""
    is_reserved = _is_reserved_id(cell_id_4)

    if not repeaters:
        css_class = "hex-free"
        if is_reserved:
            css_class += " hex-reserved"
        on_click = f'showAvailableInfo("{cell_id_4}")'
    elif len(repeaters) == 1:
        css_class = "hex-used"
        info_json = _build_info_json(repeaters)
        on_click = f'showRepeaterInfo("{cell_id_4}", {info_json})'
    else:
        css_class = "hex-duplicate"
        info_json = _build_info_json(repeaters)
        on_click = f'showDuplicateInfo("{cell_id_4}", {info_json})'

    if repeaters and not any(r.status in [NodeStatus.ACTIVE, NodeStatus.NEW] for r in repeaters):
        css_class += " hex-inactive"

    if is_reserved and repeaters:
        css_class += " hex-reserved-in-use"

    return {
        "id": cell_id_4,
        "css_class": css_class,
        "onclick_js_action": on_click,
        "search_infos": _build_search_infos(repeaters),
        "search_text": _build_search_text(repeaters),
    }


def _build_sub_matrix(prefix_2: str, repeaters: list[Node]) -> dict:
    """Build a 16x16 sub-matrix for chars 3 & 4 given a 2-char prefix."""
    sub_matrix = {}
    for row_char in _hex_chars():
        row_cells = {}
        for col_char in _hex_chars():
            cell_id_4 = f"{prefix_2}{row_char}{col_char}"
            matching = [r for r in repeaters if _get_4char_id(r) == cell_id_4]
            row_cells[col_char] = _build_sub_cell(cell_id_4, matching)
        sub_matrix[row_char] = {"cells": row_cells}
    return sub_matrix


def _aggregate_css(prefix_2: str, repeaters: list[Node]) -> str:
    """Determine primary grid cell CSS based on all repeaters under a 2-char prefix."""
    if not repeaters:
        css = "hex-free"
        if prefix_2 in reserved_ids:
            css += " hex-reserved"
        return css

    id_counts = {}
    for repeater in repeaters:
        rid = _get_4char_id(repeater)
        id_counts[rid] = id_counts.get(rid, 0) + 1

    css = "hex-duplicate" if any(count > 1 for count in id_counts.values()) else "hex-used"

    has_active = any(r.status in [NodeStatus.ACTIVE, NodeStatus.NEW] for r in repeaters)
    if not has_active:
        css += " hex-inactive"

    if prefix_2 in reserved_ids or any(_is_reserved_id(_get_4char_id(r)) for r in repeaters):
        css += " hex-reserved-in-use"

    return css


def _build_matrix(repeaters: list[Node]) -> dict:
    """
    Two-level matrix:
      primary key = first 2 hex chars
      each value has:
        - css_class: aggregate status for the primary cell
        - sub_matrix: 16x16 dict for chars 3 & 4
        - count: number of repeaters under this prefix
    """
    matrix = {}
    for row_char in _hex_chars():
        row_data = {}
        for col_char in _hex_chars():
            prefix_2 = f"{row_char}{col_char}"
            matching = [r for r in repeaters if _get_4char_id(r).startswith(prefix_2)]
            row_data[col_char] = {
                "id": prefix_2,
                "css_class": _aggregate_css(prefix_2, matching),
                "count": len(matching),
                "sub_matrix": _build_sub_matrix(prefix_2, matching),
            }
        matrix[row_char] = {"cells": row_data}
    return matrix


@prefix_matrix.route("/", methods=[FLASK_GET])
def index():
    repeaters: list[Node] = get_denver_repeaters()
    matrix_data = _build_matrix(repeaters)

    return render_template(
        'prefix_matrix.html',
        matrix_data=matrix_data,
        hex_chars=_hex_chars(),
    )
