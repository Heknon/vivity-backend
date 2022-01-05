from __future__ import annotations

from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, businesses_collection
import database.business.business as business


class Contact(DocumentObject):
    LONG_TO_SHORT = {
        "phone": 'ph',
        'email': 'ml',
        'instagram': 'ig',
        'twitter': 'tw',
        'facebook': 'fb'
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            phone: str,
            email: str,
            instagram: str,
            twitter: str,
            facebook: str
    ):
        self.business_id = business_id
        self.phone = phone
        self.email = email
        self.instagram = instagram
        self.twitter = twitter
        self.facebook = facebook

        self.updatable_fields = {
            "phone", "email", "instagram", "twitter", "facebook"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$set": {f"cntc.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda name, value: name in self.updatable_fields, kwargs.items())
        update_dict = {
            f"cntc.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_db_repr(contact: Contact):
        res = {value: getattr(contact, key) for key, value in Contact.LONG_TO_SHORT.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> Contact:
        args = {key: doc[value] for key, value in Contact.LONG_TO_SHORT.items()}
        args["business_id"] = kwargs["business_id"]

        return Contact(**args)

    def shorten_field_name(self, field_name):
        return Contact.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Contact.SHORT_TO_LONG.get(field_name, None)
