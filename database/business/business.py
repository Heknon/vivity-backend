from __future__ import annotations

from database import DocumentObject


class Business(DocumentObject):
    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        pass

    def shorten_field_name(self, field_name):
        pass

    def lengthen_field_name(self, field_name):
        pass