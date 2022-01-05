from __future__ import annotations

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

    @staticmethod
    def get_db_repr(location: Location):
        res = {value: getattr(location, key) for key, value in Location.LONG_TO_SHORT.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Location.LONG_TO_SHORT.items()}

        return Location(**args)

    def shorten_field_name(self, field_name):
        return Location.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Location.SHO.get(field_name, None)
