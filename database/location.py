from __future__ import annotations

import jsonpickle

from database import DocumentObject


class Location(DocumentObject):
    LONG_TO_SHORT = {
        "longitude": "li",
        "latitude": "lt"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            longitude: float,
            latitude: float
    ):
        self.longitude = longitude
        self.latitude = latitude

    def __repr__(self):
        return jsonpickle.encode(Location.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(location: Location, get_long_names: bool = False):
        res = {value: getattr(location, key) for key, value in Location.LONG_TO_SHORT.items()}

        if get_long_names:
            res = {location.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Location.LONG_TO_SHORT.items()}

        return Location(**args)

    def shorten_field_name(self, field_name):
        return Location.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Location.SHORT_TO_LONG.get(field_name, None)

    def __hash__(self):
        return self.longitude.__hash__() + self.latitude.__hash__()

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.longitude == other.longitude and self.latitude == other.latitude
        else:
            return False
