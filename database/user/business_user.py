from __future__ import annotations

from typing import List

from bson import ObjectId

import database.user.liked_items as liked_items_module
import database.user.shipping_address as shipping_address
import database.user.user_options as user_options
from database import User


class BusinessUser(User):
    LONG_TO_SHORT = {
        "_id": "_id",
        "email": "ml",
        "name": "nm",
        "phone": "ph",
        "password": "pw",
        "options": "op",
        "shipping_addresses": "sa",
        "order_history": "oh",
        "liked_items": "lk",
        "business_id": "bid",
        "business_name": "bnm"
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
            liked_items: liked_items_module.LikedItems,
            business_id: ObjectId,
            business_name: str
    ):
        super().__init__(_id, email, name, phone, password, options, shipping_addresses, liked_items)
        self.business_id = business_id
        self.business_name = business_name

        self.updatable_fields.add("business_name")

    @staticmethod
    def get_db_repr(user: BusinessUser):
        return {
            "_id": user._id,
            "ml": user.email,
            "nm": user.name,
            "ph": user.phone,
            "pw": user.password,
            "op": user_options.UserOptions.get_db_repr(user.options),
            "sa": list(map(lambda address: shipping_address.ShippingAddress.get_db_repr(address), user.shipping_addresses)),
            "lk": liked_items_module.LikedItems.get_db_repr(user.liked_items),
            "bid": user.business_id,
            "bnm": user.business_name
        }

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> BusinessUser:
        return BusinessUser(
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
            business_id=doc["bid"],
            business_name=doc["bnm"]
        )
