from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.business as business
import database.business.item.item as item_module
from database import DocumentObject, businesses_collection, items_collection


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
        self.items = None

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

    def update_fields(
            self,
            name: str,
            added_ids: List[ObjectId],
            removed_ids: List[ObjectId],

    ):
        return Category.document_repr_to_object(businesses_collection.find_one_and_update(
            {"_id": self.business_id, "cat": {"$elemMatch": {"name": self.name}}},
            {
                "$set": {
                    "cat.$.nm": name if name is not None else self.name,
                },
                "$pullAll": {
                    "cat.$.iti": removed_ids
                } if len(removed_ids) > 0 else {},
                "$addToSet": {
                    "cat.$.iti": {"$each": added_ids}
                } if len(added_ids) > 0 else {},
            },
            upsert=False,
            return_document=ReturnDocument.AFTER
        ))

    def get_items(self):
        return list(map(
            lambda doc: item_module.Item.document_repr_to_object(doc),
            items_collection.find_one({"_id": {"$in": self.items_ids}})
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
        return jsonpickle.encode(Category.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(category: Category, get_long_names: bool = False):
        res = {value: getattr(category, key) for key, value in Category.LONG_TO_SHORT.items()}

        if get_long_names:
            res = {category.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Category.LONG_TO_SHORT.items()}
        args["business_id"] = kwargs.get("business_id", None)

        return Category(**args)

    def shorten_field_name(self, field_name):
        return Category.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Category.SHORT_TO_LONG.get(field_name, None)
