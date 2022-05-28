from __future__ import annotations

import jsonpickle


class Location:
    def __init__(
            self,
            latitude: float,
            longitude: float
    ):
        self.longitude = longitude
        self.latitude = latitude

    def __repr__(self):
        return jsonpickle.encode(Location.get_db_repr(self), unpicklable=False)

    @staticmethod
    def get_db_repr(location: Location, get_long_names: bool = False):
        return {
            "type": "Point",
            "coordinates": [location.latitude, location.longitude]
        } if not get_long_names else [location.latitude, location.longitude]

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return Location(doc['coordinates'][0], doc['coordinates'][1])

    def __getstate__(self):
        return Location.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __hash__(self):
        return self.longitude.__hash__() + self.latitude.__hash__()

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.longitude == other.longitude and self.latitude == other.latitude
        else:
            return False
