from coloradomesh.meshcore.models.general import Node
from coloradomesh.meshcore.services.nodes import get_colorado_nodes


def prepare_contacts() -> dict:
    """
    Prepare a JSON object containing contacts in Colorado.
    """
    nodes: list[Node] = get_colorado_nodes()
    contacts = []
    for node in nodes:
        contacts.append({
            "type": node.node_type.value,
            "name": node.name,
            "custom_name": None,
            "public_key": node.public_key,
            "flags": 0,
            # needs to be strings
            "latitude": str(node.latitude),
            "longitude": str(node.longitude),
            "last_advert": node.last_heard,
            "last_modified": node.last_heard,
            "out_path": None,
        })
    return {"contacts": contacts}
