from __future__ import annotations

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, users_collection
import database.user as user


class ShippingAddress(DocumentObject):
    LONG_TO_SHORT = {
        "phone": "ph",
        "email": "ml",
        "zip_code": "zp",
        "house_number": "hn",
        "street": "st",
        "city": "ct",
        "country": "cty",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            phone: str,
            email: str,
            zip_code: str,
            house_number: str,
            street: str,
            city: str,
            country: str,
            user_id: ObjectId = None,
            address_id: int = None,
    ):
        self.user_id = user_id
        self.address_id = address_id
        self.phone = phone
        self.email = email
        self.zip_code = zip_code
        self.house_number = house_number
        self.street = street
        self.city = city
        self.country = country

        self.updatable_fields = {
            "phone", "email", "zip_code",
            "house_number", "street", "city", "country"
        }

        self.generate_update_methods()

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> user.User:
        return user.User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": ObjectId(self.user_id)},
                {"$set": {"sa." + str(self.address_id) + "." + field_name: value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> user.User:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"sa.{str(self.address_id)}.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return user.User.document_repr_to_object(
            users_collection.find_one_and_update({"_id": ObjectId(self.user_id)}, {"$set": update_dict}, return_document=ReturnDocument.AFTER)
        )

    def __repr__(self):
        return jsonpickle.encode(ShippingAddress.get_db_repr(self), unpicklable=False)

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return ShippingAddress(
            user_id=kwargs["_id"],
            address_id=kwargs["address_index"],
            phone=doc.ph,
            email=doc.ml,
            zip_code=doc.zp,
            house_number=doc.hn,
            street=doc.st,
            city=doc.ct,
            country=doc.cty,
        )

    @staticmethod
    def add_address(self, address: ShippingAddress) -> user.User:
        return user.User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self.user_id},
                {"$push": {"sa": ShippingAddress.get_db_repr(address)}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def remove_address(self, address_index) -> user.User:
        users_collection.update_one({"_id": self.user_id}, {"$unset": {"sa." + str(address_index): 1}})
        return user.User.document_repr_to_object(
            users_collection.find_one_and_update({"_id": self.user_id}, {"$pull": {"sa": None}}, return_document=ReturnDocument.AFTER)
        )

    @staticmethod
    def default_object_repr() -> list:
        return []

    @staticmethod
    def get_db_repr(address: ShippingAddress):
        return {
            "ph": address.phone,
            "ml": address.email,
            "zp": address.zip_code,
            "hn": address.house_number,
            "st": address.street,
            "ct": address.city,
            "cty": address.country
        }

    def shorten_field_name(self, field_name):
        return ShippingAddress.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ShippingAddress.SHORT_TO_LONG.get(field_name, None)
