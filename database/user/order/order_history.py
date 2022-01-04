from __future__ import annotations

import datetime
from typing import List

from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, orders_collection
from database.user.order import Order


class OrderHistory(DocumentObject):
    LONG_TO_SHORT = {
        "orders": "ods",
        "owner_id": "_id"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(self, owner_id: bytes, orders: List[Order]):
        self.owner_id = owner_id
        self.orders = orders

    @staticmethod
    def get_by_id(owner_id):
        order_history = orders_collection.find_one({"_id": ObjectId(owner_id)})
        return OrderHistory.document_repr_to_object(order_history) if order_history is not None else None

    def add_order(self, order: Order) -> OrderHistory:
        return OrderHistory.document_repr_to_object(
            orders_collection.find_one_and_update(
                {"_id": self.owner_id}, {"$addToSet": {"ods": Order.get_db_repr(order)}}, upsert=True, return_document=ReturnDocument.AFTER
            )
        )

    def remove_order(self, order_date: datetime.datetime) -> OrderHistory:
        return OrderHistory.document_repr_to_object(
            orders_collection.find_one_and_update(
                {"_id": self.owner_id}, {"$pull": {"ods.$.ots": order_date.timestamp()}}, return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_db_repr(order_history: OrderHistory):
        res = {value: getattr(order_history, key) for key, value in Order.LONG_TO_SHORT.items()}
        res.setdefault("ods", [])
        res["ods"] = list(map(lambda order: Order.get_db_repr(order), res["ods"]))

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs) -> OrderHistory:
        return OrderHistory(
            owner_id=doc["_id"].binary,
            orders=list(map(lambda order_doc: Order.document_repr_to_object(order_doc), doc.get("ods", [])))
        )

    def shorten_field_name(self, field_name):
        return OrderHistory.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return OrderHistory.SHORT_TO_LONG.get(field_name, None)
