from __future__ import annotations

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.user as user
from database import DocumentObject, users_collection


class ShippingAddress(DocumentObject):
    LONG_TO_SHORT = {
        "phone": "ph",
        "name": "nm",
        "zip_code": "zp",
        "street": "st",
        "city": "ct",
        "country": "cty",
        "province": "prv",
        "extra_info": "etc"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            name: str,
            phone: str,
            zip_code: str,
            province: str,
            extra_info: str,
            street: str,
            city: str,
            country: str,
            user_id: ObjectId = None,
            address_id: int = None,
    ):
        self.user_id = user_id
        self.address_id = address_id
        self.name = name
        self.phone = phone
        self.province = province
        self.extra_info = extra_info
        self.zip_code = zip_code
        self.street = street
        self.city = city
        self.country = country

        self.updatable_fields = {
            "phone", "email", "zip_code",
            "street", "city", "country", "extra_info", "province", "name"
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
        return jsonpickle.encode(ShippingAddress.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return ShippingAddress(
            user_id=kwargs["_id"] if "_id" in kwargs else None,
            address_id=kwargs["address_index"],
            phone=doc['ph'],
            zip_code=doc['zp'],
            street=doc['st'],
            city=doc['ct'],
            country=doc['cty'],
            province=doc["prv"],
            extra_info=doc["etc"],
            name=doc["nm"]
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
    def get_db_repr(address: ShippingAddress, get_long_names: bool = False):
        res = {
            "ph": address.phone.strip(),
            "zp": address.zip_code.strip(),
            "st": address.street.strip(),
            "ct": address.city.strip(),
            "cty": address.country.strip(),
            "etc": address.extra_info.strip(),
            "prv": address.province.strip(),
            "nm": address.name.strip()
        }

        if get_long_names:
            res = {address.lengthen_field_name(key): value for key, value in res.items()}

        return res

    def shorten_field_name(self, field_name):
        return ShippingAddress.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ShippingAddress.SHORT_TO_LONG.get(field_name, None)

    def __getstate__(self):
        return ShippingAddress.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
