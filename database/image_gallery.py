from __future__ import annotations

from database import DocumentObject


class ImageGallery(DocumentObject):
    LONG_TO_SHORT = {

    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(self):
        pass

    @staticmethod
    def get_db_repr(image_gallery: ImageGallery):
        pass

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        pass

    def shorten_field_name(self, field_name):
        pass

    def lengthen_field_name(self, field_name):
        pass
