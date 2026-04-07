from coloradomesh.meshcore.services.stats import Stats


class StatsService:
    def __init__(self):
        self._stats_service = Stats()

    def refresh_data(self) -> None:
        self._stats_service.refresh_data()

    def get_node_count(self) -> int:
        return self._stats_service.get_node_count()

    def get_repeater_count(self) -> int:
        return self._stats_service.get_repeater_count()

    def get_room_count(self) -> int:
        return self._stats_service.get_room_count()

    def get_companion_count(self) -> int:
        return self._stats_service.get_companion_count()

    def get_node_count_by_region(self) -> dict[str, int]:
        return self._stats_service.get_node_count_by_region()
