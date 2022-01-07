from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

import database.user.liked_items as liked_items_module
import database.user.shipping_address as shipping_address
import database.user.user_options as user_options
from database import users_collection, Image
import database.user.user as user_module


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
        "profile_picture": "pfp"
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
            business_id: ObjectId
    ):
        super().__init__(_id, email, name, phone, profile_picture, password, options, shipping_addresses, liked_items)
        self.business_id = business_id

    def __repr__(self):
        return jsonpickle.encode(BusinessUser.get_db_repr(self), unpicklable=False)

    @staticmethod
    def get_by_email(email, raw_document=True) -> BusinessUser | dict | None:
        return users_collection.find_one({"email": email}) \
            if raw_document else BusinessUser.document_repr_to_object(users_collection.find_one({"email": email}))

    @staticmethod
    def get_by_id(_id: ObjectId, raw_document=True) -> BusinessUser | dict | None:
        return users_collection.find_one({"_id": _id}) \
            if raw_document else BusinessUser.document_repr_to_object(users_collection.find_one({"_id": _id}))

    @staticmethod
    def get_db_repr(user: BusinessUser):
        res = {value: getattr(user, key) for key, value in BusinessUser.LONG_TO_SHORT.items()}

        res["pfp"] = res["pfp"].image_id
        res["op"] = user_options.UserOptions.get_db_repr(user.options)
        res["sa"] = list(map(lambda address: shipping_address.ShippingAddress.get_db_repr(address), user.shipping_addresses))
        res["lk"] = liked_items_module.LikedItems.get_db_repr(user.liked_items)

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> BusinessUser:
        args = {key: doc[value] for key, value in BusinessUser.LONG_TO_SHORT.items()}

        args["profile_picture"] = Image(doc.get("pfp", None))
        args["options"] = user_options.UserOptions.document_repr_to_object(doc["op"], _id=doc["_id"]) if doc.get("op", None) is not None else None
        args["shipping_addresses"] = list(
            map(
                lambda i, sa: shipping_address.ShippingAddress.document_repr_to_object(sa, _id=doc["_id"], address_index=i),
                enumerate(doc.get("sa", []))
            )
        )
        args["liked_items"] = \
            liked_items_module.LikedItems.document_repr_to_object(doc["lk"], _id=doc["_id"]) if doc.get("lk", None) is not None else None

        return BusinessUser(**args)
