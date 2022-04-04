from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

from database import DocumentObject
from database.business.item import SelectedModificationButton


class OrderItem(DocumentObject):
    LONG_TO_SHORT = {
        "item_id": "iid",
        "price": "p",
        "selected_modifiers": "sm",
        "amount": "amt",
        "business_id": "bid"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            business_id: ObjectId,
            amount: int,
            price: float,
            selected_modifiers: List[SelectedModificationButton]
    ):
        self.item_id = item_id
        self.business_id = business_id
        self.amount = amount
        self.price = price
        self.selected_modifiers = selected_modifiers

    def __repr__(self):
        return jsonpickle.encode(OrderItem.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(
            order_item: OrderItem,
            get_long_names: bool = False
    ) -> dict:
        res = {value: getattr(order_item, key) for key, value in OrderItem.LONG_TO_SHORT.items()}
        res.setdefault("sm", [])
        res["sm"] = list(map(lambda sm: SelectedModificationButton.get_db_repr(sm, get_long_names), res["sm"]))

        if get_long_names:
            res["bid"] = str(res["bid"])
            res["iid"] = str(res["iid"])
            res = {order_item.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in OrderItem.LONG_TO_SHORT.items()}
        args.setdefault("selected_modifiers", [])
        args["selected_modifiers"] = \
            list(map(lambda mod_button: SelectedModificationButton.document_repr_to_object(mod_button), args["selected_modifiers"]))

        return OrderItem(**args)

    def shorten_field_name(self, field_name):
        return OrderItem.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return OrderItem.SHORT_TO_LONG.get(field_name, None)
