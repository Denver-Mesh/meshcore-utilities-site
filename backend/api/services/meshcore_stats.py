from coloradomesh.meshcore.models.general import Node, NodeType, Regions
from coloradomesh.meshcore.services.nodes import get_colorado_nodes

from geopy.distance import geodesic as GD

def _filter_nodes_of_type(nodes: list[Node], node_type: NodeType) -> list[Node]:
    return [node for node in nodes if node.node_type == node_type]


def _determine_region_for_node(node: Node) -> Regions:
    # Until we collect actual region codes from the nodes, we have to guess based on its location
    lat, long = node.latitude, node.longitude
    shortest_distance = None
    nearest_region = None

    for region in Regions:
        airport = region.value.airport
        airport_location = (airport.latitude, airport.longitude)
        distance = GD((lat, long), airport_location).km
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            nearest_region = region

    return nearest_region or list(Regions)[0]


class NodeRegionMapEntry:
    def __init__(self, node: Node, region: Regions):
        self.node = node
        self.region = region


class StatsService:
    def __init__(self):
        self._nodes: list[Node] = []
        self._repeaters: list[Node] = []
        self._rooms: list[Node] = []
        self._companions: list[Node] = []
        self._node_region_map: dict[str, NodeRegionMapEntry] = {}

        self.refresh_data()

    def _parse_nodes(self) -> None:
        self._repeaters = _filter_nodes_of_type(self._nodes, NodeType.REPEATER)
        self._rooms = _filter_nodes_of_type(self._nodes, NodeType.ROOM_SERVER)
        self._companions = _filter_nodes_of_type(self._nodes, NodeType.COMPANION)

        self._node_region_map = {
            node.public_key: NodeRegionMapEntry(node, _determine_region_for_node(node))
            for node in self._nodes
        }

    def refresh_data(self) -> None:
        self._nodes = get_colorado_nodes()
        self._parse_nodes()

    def get_node_count(self) -> int:
        return len(self._nodes)

    def get_repeater_count(self) -> int:
        return len(self._repeaters)

    def get_room_count(self) -> int:
        return len(self._rooms)

    def get_companion_count(self) -> int:
        return len(self._companions)

    def get_node_count_by_region(self) -> dict[str, int]:
        region_counts: dict[str, int] = {region.code.upper(): 0 for region in Regions}
        for entry in self._node_region_map.values():
            region_counts[entry.region.code.upper()] += 1
        return region_counts
