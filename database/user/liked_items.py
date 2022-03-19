from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.user.user as user
from database import users_collection, DocumentObject


class LikedItems(DocumentObject):
    def __init__(
            self,
            user_id: ObjectId,
            liked_items: List[ObjectId]
    ):
        self.user_id = user_id
        self._liked_items = liked_items

    def __iter__(self):
        return self._liked_items

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return LikedItems(liked_items=doc, user_id=kwargs["_id"])

    def add_liked_item(self, item_id: bytes) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {"lk": item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def add_liked_items(self, *item_id: ObjectId) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {"lk": {"$each": item_id}}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def remove_liked_item(self, item_id: ObjectId) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$pull": {"lk": item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def remove_liked_items(self, *item_id: ObjectId) -> user.User:
        res = user.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$pullAll": {"lk": item_id}},
            return_document=ReturnDocument.AFTER
        ))

        return res

    def __repr__(self):
        return jsonpickle.encode(LikedItems.get_db_repr(self), unpicklable=False)

    def __getstate__(self):
        return LikedItems.get_db_repr(self)

    def __setstate__(self, state):
        self.__dict__.update(state)

    @staticmethod
    def default_object_repr() -> list:
        return []

    def get_db_repr(self):
        return self._liked_items

    def shorten_field_name(self, field_name):
        return None

    def lengthen_field_name(self, field_name):
        return None
