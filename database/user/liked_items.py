from typing import List, Dict

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import users_collection, DocumentObject
import database.user.user as user


class LikedItems(DocumentObject):
    def __init__(
            self,
            user_id: ObjectId,
            liked_items: Dict[bytes, List[int]]
    ):
        self.user_id = user_id
        self._liked_items = liked_items

    def __iter__(self):
        return self._liked_items.items()

    def __getitem__(self, item):
        return self._liked_items.get(item, None)

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return LikedItems(liked_items=doc, user_id=kwargs["_id"])

    def add_liked_item(self, owning_business_id: ObjectId, item_id: int) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {"lk." + owning_business_id.binary.decode("cp437"): item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def add_liked_items(self, owning_business_id: ObjectId, *item_id: int) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {"lk." + owning_business_id.binary.decode("cp437"): {"$each": item_id}}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def remove_liked_item(self, owning_business_id: ObjectId, item_id: int) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$pull": {"lk." + owning_business_id.binary.decode("cp437"): item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def remove_liked_items(self, owning_business_id: ObjectId, *item_id: int) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$pullAll": {"lk." + owning_business_id.binary.decode("cp437"): item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def __repr__(self):
        return jsonpickle.encode(LikedItems.get_db_repr(self), unpicklable=False)

    @staticmethod
    def default_object_repr() -> dict:
        return {}

    def get_db_repr(self):
        return self._liked_items

    def shorten_field_name(self, field_name):
        return None

    def lengthen_field_name(self, field_name):
        return None
