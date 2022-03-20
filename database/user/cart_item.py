from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

from database import DocumentObject, Image
from database.business.item import SelectedModificationButton


class CartItem(DocumentObject):
    LONG_TO_SHORT = {
        "item_id": "iid",
        "amount": "amt",
        "modifiers_chosen": "mc",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            amount: int,
            modifiers_chosen: List[SelectedModificationButton]
    ):
        self.item_id = item_id
        self.amount = amount
        self.modifiers_chosen = modifiers_chosen

    def __repr__(self):
        return jsonpickle.encode(CartItem.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(
            cart_item: CartItem,
            get_long_names: bool = False
    ) -> dict:
        res = {value: getattr(cart_item, key) for key, value in CartItem.LONG_TO_SHORT.items()}
        res.setdefault("mc", [])
        res["mc"] = list(map(lambda smb: SelectedModificationButton.get_db_repr(smb, get_long_names), res["mc"]))

        if get_long_names:
            res["iid"] = str(res["iid"])
            res = {cart_item.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in CartItem.LONG_TO_SHORT.items()}
        args.setdefault("modifiers_chosen", [])
        args["modifiers_chosen"] = \
            list(map(lambda mod_button: SelectedModificationButton.document_repr_to_object(mod_button), args["modifiers_chosen"]))

        return CartItem(**args)

    def shorten_field_name(self, field_name):
        return CartItem.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return CartItem.SHORT_TO_LONG.get(field_name, None)
