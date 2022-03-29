from __future__ import annotations

import datetime
from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, orders_collection
from database.user.order import OrderItem


class Order(DocumentObject):
    LONG_TO_SHORT = {
        "order_date": "ots",
        "items": "it"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            order_date: datetime.datetime,
            items: List[OrderItem],
    ):
        self._id = _id
        self.order_date = order_date
        self.items = items

    @staticmethod
    def save(order: Order):
        order_save = Order(
            _id=ObjectId(),
            order_date=order.order_date,
            items=order.items
        )
        saved = Order.get_db_repr(order_save)
        Order.document_repr_to_object(orders_collection.find_one_and_update(
            {"_id": order_save._id},
            saved,
            upsert=True,
            return_document=ReturnDocument.AFTER
        ))

    @staticmethod
    def get_db_repr(order: Order, get_long_names: bool = False):
        res = {value: getattr(order, key) for key, value in Order.LONG_TO_SHORT.items()}
        res["ots"] = res["ots"].timestamp()
        res.setdefault("it", [])
        res["it"] = list(map(lambda order_item: OrderItem.get_db_repr(order_item), res["it"]))

        if get_long_names:
            res = {order.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return Order(
            order_date=datetime.datetime.fromtimestamp(doc["ots"]),
            items=list(map(lambda order_item: OrderItem.document_repr_to_object(order_item), doc.get("it", [])))
        )

    def __repr__(self):
        return jsonpickle.encode(Order.get_db_repr(self, True), unpicklable=False)

    def __getstate__(self):
        res = Order.get_db_repr(self, True)
        return res

    def __setstate__(self, state):
        self.__dict__.update(state)

    def shorten_field_name(self, field_name):
        return Order.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Order.SHORT_TO_LONG.get(field_name, None)
