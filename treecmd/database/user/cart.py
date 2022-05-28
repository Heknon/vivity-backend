from __future__ import annotations

from typing import List, Dict

from bson import ObjectId
from pymongo import ReturnDocument

import database.business.item.item as item_module
import database.user.cart_item as cart_item_module
import database.user.user as user_module
from database import users_collection


class Cart:
    def __init__(
            self,
            user_id: ObjectId,
            items: List[cart_item_module.CartItem],
    ):
        self.user_id = user_id
        self.items = items
        self.db_prefix = "crt"

    def get_full_items(self):
        return item_module.Item.get_items(*list(map(lambda i: i.item_id, self.items)))

    def replace_items(self, items: List[cart_item_module.CartItem]):
        db_items = list(map(lambda item: cart_item_module.CartItem.get_db_repr(item), items))
        return user_module.User.document_repr_to_object(users_collection.find_one_and_update({"_id": self.user_id}, {
            "$set": {self.db_prefix: db_items}
        }, return_document=ReturnDocument.AFTER))

    def remove(self, index):
        users_collection.update_one({"_id": self.user_id}, {
            "$set": {f"{self.db_prefix}.{index}": 1}
        })

        return user_module.User.document_repr_to_object(users_collection.find_one_and_update({"_id": self.user_id}, {
            "$pull": {self.db_prefix: None}
        }, return_document=ReturnDocument.AFTER))

    def mass_remove(self, *index):
        unsetDict = {f"{self.db_prefix}.{index}": 1 for index in index}

        users_collection.update_one({"_id": self.user_id}, {
            "$unset": unsetDict
        })

        return user_module.User.document_repr_to_object(users_collection.find_one_and_update({"_id": self.user_id}, {
            "$pull": {self.db_prefix: None}
        }, return_document=ReturnDocument.AFTER))

    def add_item(self, cart_item: cart_item_module.CartItem):
        return user_module.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {self.db_prefix: cart_item_module.CartItem.get_db_repr(cart_item)}},
            return_document=ReturnDocument.AFTER
        ))

    def add_items(self, *cart_item: cart_item_module.CartItem):
        items = list(map(lambda item: cart_item_module.CartItem.get_db_repr(item), cart_item))

        return user_module.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$addToSet": {self.db_prefix: {"$each": items}}},
            return_document=ReturnDocument.AFTER
        ))

    def update_quantity(self, index: int, quantity: int):
        return user_module.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$set": {f"{self.db_prefix}.{index}.amt": quantity}},
            return_document=ReturnDocument.AFTER
        ))

    def mass_update_quantity(self, quantities: Dict[int, int]):
        setDict = {f"{self.db_prefix}.{index}.amt": quantity for index, quantity in quantities.items()}

        return user_module.User.document_repr_to_object(users_collection.find_one_and_update(
            {"_id": self.user_id},
            {"$set": setDict},
            return_document=ReturnDocument.AFTER
        ))

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        items = list(map(lambda cart_item_doc: cart_item_module.CartItem.document_repr_to_object(cart_item_doc), doc))

        user_id = kwargs.get("_id", None)

        return Cart(user_id=user_id, items=items)

    @staticmethod
    def get_db_repr(
            cart: Cart,
            get_long_names: bool = False
    ):
        return list(map(lambda cart_item: cart_item_module.CartItem.get_db_repr(cart_item, get_long_names), cart.items))

    def __getstate__(self):
        return Cart.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
