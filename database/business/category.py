from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.business as business
import database.business.item.item as item_module
from database import DocumentObject, businesses_collection


class Category(DocumentObject):
    LONG_TO_SHORT = {
        "name": "nm",
        "item_ids": "iti"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            name: str,
            items_ids: List[ObjectId]
    ):
        self.business_id = business_id
        self.name = name
        self.items_ids = items_ids

        self.updatable_fields = {
            "name"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$set": {f"cat.$.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"cat.$.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$set": update_dict},
                return_document=ReturnDocument.AFTER
            )
        )

    def get_items(self):
        accepts = {f"it.{item_id.binary.decode('cp437')}": 1 for item_id in self.items_ids}
        accepts["_id"] = 0

        return list(map(
            lambda doc: item_module.Item.document_repr_to_object(doc),
            businesses_collection.find_one({"_id": self.business_id}, **accepts)["it"].values()
        ))

    def add_item(self, item_id: ObjectId):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$addToSet": {f"cat.$.iti": item_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def add_items(self, *item_ids: ObjectId):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$addToSet": {f"cat.$.iti": {"$each": item_ids}}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_item(self, item_id: ObjectId):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$pull": {f"cat.$.iti": item_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_items(self, *item_ids: ObjectId):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
                {"$pullAll": {f"cat.$.iti": item_ids}},
                return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(Category.get_db_repr(self), unpicklable=False)

    @staticmethod
    def get_db_repr(category: Category):
        res = {value: getattr(category, key) for key, value in Category.LONG_TO_SHORT.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Category.LONG_TO_SHORT.items()}
        args["business_id"] = kwargs["business_id"]

        return Category(**args)

    def shorten_field_name(self, field_name):
        return Category.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Category.SHORT_TO_LONG.get(field_name, None)
