from __future__ import annotations

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.user as user
import database.user.unit as units
from database import DocumentObject, users_collection


class UserOptions(DocumentObject):
    LONG_TO_SHORT = {
        "unit": "u",
        "currency_type": "ct",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            user_id: ObjectId,
            unit: units.Unit,
            currency_type: str,
    ):
        self.user_id = user_id
        self.unit = unit
        self.currency_type = currency_type

        self.updatable_fields = {
            "distance_unit", "currency_type"
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

    def update_fields(
            self,
            unit: units.Unit,
            currency_type: str,
            email: str,
            phone: str,
    ) -> user.User:
        set_dict = {}
        if unit is not None:
            set_dict["u"] = unit.value

        if currency_type is not None:
            set_dict['ct'] = currency_type

        return user.User.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": ObjectId(self.user_id)}, {"$set": set_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(UserOptions.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> UserOptions:
        args = {key: doc[value] for key, value in UserOptions.LONG_TO_SHORT.items()}
        args["unit"] = units.Unit._value2member_map_[doc['u']]

        return UserOptions(**args, user_id=kwargs["_id"])

    @staticmethod
    def default_object_repr() -> dict:
        return {
            "u": units.Unit.Metric.value,
            "ct": "ils",
        }

    @staticmethod
    def get_db_repr(options: UserOptions, get_long_names: bool = False):
        res = {value: getattr(options, key) for key, value in UserOptions.LONG_TO_SHORT.items()}
        res["u"] = options.unit.value

        if get_long_names:
            res = {options.lengthen_field_name(key): value for key, value in res.items()}

        return res

    def shorten_field_name(self, field_name):
        return UserOptions.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return UserOptions.SHORT_TO_LONG.get(field_name, None)

    def __getstate__(self):
        return UserOptions.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
