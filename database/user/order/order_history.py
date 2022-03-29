from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import orders_collection, users_collection
from database.user.order import Order


class OrderHistory:
    def __init__(self, user_id: bytes, orders: List[ObjectId]):
        self.user_id = user_id
        self.orders = orders

    def get_orders(self):
        return list(map(lambda doc: Order.document_repr_to_object(doc), orders_collection.find({"_id": {"$in": self.orders}})))

    def add_order(self, order_id: ObjectId) -> OrderHistory:
        return OrderHistory.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self.user_id}, {"$addToSet": {"odh": order_id}}, return_document=ReturnDocument.AFTER
            )
        )

    def remove_order(self, order_id: ObjectId) -> OrderHistory:
        return OrderHistory.document_repr_to_object(
            users_collection.find_one_and_update(
                {"_id": self.user_id}, {"$pull": {"odh": order_id}}, return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(OrderHistory.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(order_history: OrderHistory, get_long_names: bool = False):
        return order_history.orders if not get_long_names else list(map(str, order_history.orders))

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> OrderHistory:
        return OrderHistory(
            user_id=kwargs["_id"],
            orders=doc
        )

    def __getstate__(self):
        return OrderHistory.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
