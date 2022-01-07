from __future__ import annotations

import jsonpickle

import database.doc_object as doc_object


class Color(doc_object.DocumentObject):
    def __init__(self, rgb: bytes):
        self.rgb = rgb
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]

    def __repr__(self):
        return jsonpickle.encode(Color.get_db_repr(self))

    @staticmethod
    def get_db_repr(color: Color) -> bytes:
        return color.rgb

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return Color(doc)

    def shorten_field_name(self, field_name):
        pass

    def lengthen_field_name(self, field_name):
        pass
