from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

import database.user.cart as cart_module
import database.user.liked_items as liked_items_module
import database.user.order.order_history as order_history_module
import database.user.shipping_address as shipping_address
import database.user.user as user_module
import database.user.user_options as user_options
from database import users_collection, Image


class BusinessUser(user_module.User):
    LONG_TO_SHORT = {
        "_id": "_id",
        "email": "ml",
        "name": "nm",
        "phone": "ph",
        "password": "pw",
        "options": "op",
        "shipping_addresses": "sa",
        "liked_items": "lk",
        "business_id": "bid",
        "profile_picture": "pfp",
        "is_system_admin": "isa",
        "cart": "crt",
        "order_history": "odh"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            email: str,
            name: str,
            phone: str,
            password: bytes,
            profile_picture: Image,
            options: user_options.UserOptions,
            shipping_addresses: List[shipping_address.ShippingAddress],
            liked_items: liked_items_module.LikedItems,
            business_id: ObjectId,
            cart: cart_module.Cart,
            is_system_admin: bool,
            order_history: order_history_module.OrderHistory
    ):
        super().__init__(
            _id,
            email,
            name,
            phone,
            profile_picture,
            password,
            options,
            shipping_addresses,
            liked_items, cart,
            is_system_admin,
            order_history
        )
        self.business_id = business_id

    def __repr__(self):
        return jsonpickle.encode(BusinessUser.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_by_email(email, raw_document=True) -> BusinessUser | dict | None:
        return users_collection.find_one({"email": email}) \
            if raw_document else BusinessUser.document_repr_to_object(users_collection.find_one({"email": email}))

    @staticmethod
    def get_by_id(_id: ObjectId, raw_document=True) -> BusinessUser | dict | None:
        return users_collection.find_one({"_id": _id}) \
            if raw_document else BusinessUser.document_repr_to_object(users_collection.find_one({"_id": _id}))

    @staticmethod
    def get_db_repr(user: BusinessUser, get_long_names: bool = False):
        return user_module.User.get_db_repr(user)

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> BusinessUser:
        return user_module.User.document_repr_to_object(doc)
