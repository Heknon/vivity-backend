from __future__ import annotations

from typing import List

import bcrypt
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.results import DeleteResult

import database.user.liked_items as liked_items_module
import database.user.order.order_history as order_history_module
import database.user.shipping_address as shipping_address
import database.user.user_options as user_options
from database import users_collection, DocumentObject


# Todo: ADD ORDER HISTORY
class User(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "email": "ml",
        "name": "nm",
        "phone": "ph",
        "password": "pw",
        "options": "op",
        "shipping_addresses": "sa",
        "order_history": "oh",
        "liked_items": "lk"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            email: str,
            name: str,
            phone: str,
            password: str,
            options: user_options.UserOptions,
            shipping_addresses: List[shipping_address.ShippingAddress],
            liked_items: liked_items_module.LikedItems
    ):
        self._id = _id
        self.email = email
        self.name = name
        self.phone = phone
        self.password = password
        self.options = options
        self.shipping_addresses = shipping_addresses
        self.liked_items = liked_items

        self.updatable_fields = {"email", "phone", "password"}
        self.generate_update_methods()

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> User:
        return User.document_repr_to_object(
            users_collection.find_one_and_update({"_id": ObjectId(self._id)}, {"$set": {field_name: value}}, return_document=ReturnDocument.AFTER)
        )

    def insert(self) -> ObjectId:
        return users_collection.insert_one(User.get_db_repr(self)).inserted_id

    def get_order_history(self) -> order_history_module.OrderHistory | None:
        return order_history_module.OrderHistory.get_by_id(self._id)

    @staticmethod
    def get_by_email(email) -> User:
        return users_collection.find_one({"email": email})

    @staticmethod
    def get_by_id(_id: bytes) -> User:
        return users_collection.find_one({"_id": ObjectId(_id)})

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> User:
        return User(
            _id=doc["_id"],
            email=doc.ml,
            name=doc.nm,
            phone=doc.ph,
            password=doc.pw,
            options=user_options.UserOptions.document_repr_to_object(doc.op, _id=doc["_id"]),
            shipping_addresses=list(
                map(lambda i, sa: shipping_address.ShippingAddress.document_repr_to_object(sa, _id=doc["_id"], address_index=i),
                    enumerate(doc.get("sa", [])))),
            liked_items=liked_items_module.LikedItems.document_repr_to_object(doc, _id=doc["_id"]),
        )

    @staticmethod
    def create_new_user(
            email=None,
            name=None,
            phone=None,
            password=None,
            hash_password=True
    ) -> ObjectId:
        return users_collection.insert_one(User.default_object_repr(email, name, phone, password, hash_password)).inserted_id

    @staticmethod
    def default_object_repr(
            email=None,
            name=None,
            phone=None,
            password=None,
            hash_password=True
    ) -> dict:
        return {
            "email": email,
            "name": name,
            "phone": phone,
            "password": User.hash_password(password) if hash_password else password,
            "options": user_options.UserOptions.default_object_repr(),
            "shipping_addresses": shipping_address.ShippingAddress.default_object_repr(),
            "liked_items": liked_items_module.LikedItems.default_object_repr()
        }

    @staticmethod
    def get_db_repr(user: User):
        return {
            "_id": user._id,
            "ml": user.email,
            "nm": user.name,
            "ph": user.phone,
            "pw": user.password,
            "op": user_options.UserOptions.get_db_repr(user.options),
            "sa": list(map(lambda address: shipping_address.ShippingAddress.get_db_repr(address), user.shipping_addresses)),
            "lk": liked_items_module.LikedItems.get_db_repr(user.liked_items),
        }

    @staticmethod
    def delete_by_id(_id: bytes) -> DeleteResult:
        return users_collection.delete_one({"_id": _id})

    @staticmethod
    def delete_by_email(email: str) -> DeleteResult:
        return users_collection.delete_one({"email": email})

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt(16)
        return bcrypt.hashpw(password.encode(), salt)

    @staticmethod
    def compare_hash(password: str, hashed_password: bytes):
        return bcrypt.checkpw(password.encode(), hashed_password)

    def shorten_field_name(self, field_name):
        return User.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return User.SHORT_TO_LONG.get(field_name, None)
