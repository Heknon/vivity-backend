from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

from database import DocumentObject, Image
from database.business.item import SelectedModificationButton


class OrderItem(DocumentObject):
    LONG_TO_SHORT = {
        "item_id": "iid",
        "preview_image": "pi",
        "title": "ttl",
        "subtitle": "sbt",
        "description": "dsc",
        "price": "p",
        "modifiers_chosen": "mc",
        "amount": "amt"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            preview_image: Image,
            title: str,
            subtitle: str,
            description: str,
            amount: int,
            price: float,
            modifiers_chosen: List[SelectedModificationButton]
    ):
        self.item_id = item_id
        self.amount = amount
        self.price = price
        self.preview_image = preview_image
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.modifiers_chosen = modifiers_chosen

    def __repr__(self):
        return jsonpickle.encode(OrderItem.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(
            order_item: OrderItem,
            get_long_names: bool = False
    ) -> dict:
        res = {value: getattr(order_item, key) for key, value in OrderItem.LONG_TO_SHORT.items()}
        res.setdefault("mc", [])
        res["mc"] = list(map(lambda mc: SelectedModificationButton.get_db_repr(mc, get_long_names), res["mc"]))
        res["pi"] = res["pi"].image_id

        if get_long_names:
            res = {order_item.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in OrderItem.LONG_TO_SHORT.items()}
        args.setdefault("modifiers_chosen", [])
        args["modifiers_chosen"] = \
            list(map(lambda mod_button: SelectedModificationButton.document_repr_to_object(mod_button), args["modifiers_chosen"]))
        args["preview_image"] = Image(doc[args["preview_image"]])

        return OrderItem(**args)

    def shorten_field_name(self, field_name):
        return OrderItem.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return OrderItem.SHORT_TO_LONG.get(field_name, None)
