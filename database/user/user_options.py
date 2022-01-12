from __future__ import annotations

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.user as user
from database import DocumentObject, users_collection


class UserOptions(DocumentObject):
    LONG_TO_SHORT = {
        "business_search_radius": "bsr",
        "distance_unit": "du",
        "currency_type": "ct",
        "shirt_size": "shs",
        "jeans_size": "jes",
        "sweats_size": "sws",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            user_id: ObjectId,
            business_search_radius: float,
            distance_unit: str,
            currency_type: str,
            shirt_size: str,
            jeans_size: str,
            sweats_size: str
    ):
        self.user_id = user_id
        self.business_search_radius = business_search_radius
        self.distance_unit = distance_unit
        self.currency_type = currency_type
        self.shirt_size = shirt_size
        self.jeans_size = jeans_size
        self.sweats_size = sweats_size

        self.updatable_fields = {
            "business_search_radius", "distance_unit", "currency_type",
            "shirt_size", "jeans_size", "sweats_size"
        }

        self.generate_update_methods()

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> user.User:
        return user.User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": ObjectId(self.user_id)}, {"$set": {"op." + field_name: value}}, return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> user.User:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"op.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return user.User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": ObjectId(self.user_id)}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(UserOptions.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> UserOptions:
        return UserOptions(
            user_id=kwargs["_id"],
            business_search_radius=doc["bsr"],
            distance_unit=doc["du"],
            currency_type=doc["ct"],
            shirt_size=doc["shs"],
            jeans_size=doc["jes"],
            sweats_size=doc["sws"],
        )

    @staticmethod
    def default_object_repr() -> dict:
        return {
            "bsr": 3,
            "du": "km",
            "ct": "ils",
            "shs": None,
            "jes": None,
            "sws": None,
        }

    @staticmethod
    def get_db_repr(options: UserOptions, get_long_names: bool = False):
        res = {
            "bsr": options.business_search_radius,
            "du": options.distance_unit,
            "ct": options.currency_type,
            "shs": options.shirt_size,
            "jes": options.jeans_size,
            "sws": options.sweats_size
        }

        if get_long_names:
            res = {options.lengthen_field_name(key): value for key, value in res.items()}

        return res

    def shorten_field_name(self, field_name):
        return UserOptions.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return UserOptions.SHORT_TO_LONG.get(field_name, None)
