from __future__ import annotations


class UserSettings:
    def __init__(
            self,
            default_search_radius: int,
            currency: str,
            distance_unit: str,
            shirt_size: str | int,
            sweats_size: str | int
    ):
        self.default_search_radius = default_search_radius
        self.currency = currency
        self.distance_unit = distance_unit
        self.shirt_size = shirt_size
        self.sweats_size = sweats_size
