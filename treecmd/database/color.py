from __future__ import annotations

import jsonpickle

import database.doc_object as doc_object


class Color(doc_object.DocumentObject):
    def __init__(self, hexColor: int):
        self.hexColor = hexColor

    def __repr__(self):
        return jsonpickle.encode(Color.get_db_repr(self))

    @staticmethod
    def get_db_repr(color: Color) -> int:
        return color.hexColor

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return Color(doc)

    def shorten_field_name(self, field_name):
        pass

    def lengthen_field_name(self, field_name):
        pass
