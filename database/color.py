from __future__ import annotations

from database import DocumentObject


class Color(DocumentObject):
    def __init__(self, rgb: bytes):
        self.rgb = rgb
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]

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
