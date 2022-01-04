from abc import ABC


class DocumentObject(ABC):
    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        raise NotImplementedError(f"Must implement document to object representation method!")

    def shorten_field_name(self, field_name):
        raise NotImplementedError(f"Must implement field name shortening method in {type(self)}!")

    def lengthen_field_name(self, field_name):
        raise NotImplementedError(f"Must implement field name lengthening method in {type(self)}!")
