from __future__ import annotations


class UserSettings:
    def __init__(
            self,
            business_search_radius: int,
            currency_type: str,
            distance_unit: str,
            shirt_size: str | int,
            sweats_size: str | int,
            jeans_size: str | int
    ):
        self.business_search_radius = business_search_radius
        self.currency_type = currency_type
        self.distance_unit = distance_unit
        self.shirt_size = shirt_size
        self.sweats_size = sweats_size
        self.jeans_size = jeans_size
