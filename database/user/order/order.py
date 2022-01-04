from __future__ import annotations

import datetime
from typing import List

from database import DocumentObject
from database.user.order import OrderItem


class Order(DocumentObject):
    LONG_TO_SHORT = {
        "order_date": "ots",
        "items": "it"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            order_date: datetime.datetime,
            items: List[OrderItem],
    ):
        self.order_date = order_date
        self.items = items

    @staticmethod
    def get_db_repr(order: Order):
        res = {value: getattr(order, key) for key, value in Order.LONG_TO_SHORT.items()}
        res["ots"] = res["ots"].timestamp()
        res.setdefault("it", [])
        res["it"] = list(map(lambda order_item: OrderItem.get_db_repr(order_item), res["it"]))

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        return Order(
            order_date=datetime.datetime.fromtimestamp(doc["ots"]),
            items=list(map(lambda order_item: OrderItem.document_repr_to_object(order_item), doc.get("it", [])))
        )

    def shorten_field_name(self, field_name):
        return Order.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Order.SHORT_TO_LONG.get(field_name, None)
