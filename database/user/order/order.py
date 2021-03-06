from __future__ import annotations

import datetime
from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.user.shipping_address as sa_module
import database.user.shipping_method as sm_module
from database import DocumentObject, orders_collection
from .order_item import OrderItem


class Order(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "order_date": "ots",
        "subtotal": "sbt",
        "shipping_cost": "shc",
        "shipping_address": "sa",
        "cupon_discount": "cd",
        "total": "t",
        "items": "it",
        'shipping_method': 'sm'
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            order_date: datetime.datetime,
            subtotal: float,
            shipping_cost: float,
            cupon_discount: float,
            total: float,
            shipping_address: sa_module.ShippingAddress,
            items: List[OrderItem],
            shipping_method: ShippingMethod,
    ):
        self._id = _id
        self.order_date = order_date
        self.subtotal = subtotal
        self.shipping_cost = shipping_cost
        self.shipping_address = shipping_address
        self.cupon_discount = cupon_discount
        self.total = total
        self.items = items
        self.shipping_method = shipping_method

    @staticmethod
    def get_orders(order_ids: List[ObjectId], business_id: ObjectId):
        orders = list(map(lambda doc: Order.document_repr_to_object(doc), orders_collection.find({"_id": {"$in": order_ids}})))

        for order in orders:
            items = []
            for item in order.items:
                if ObjectId(item.business_id) == business_id:
                    items.append(item)

            order.items = items

        return orders

    @staticmethod
    def get_order(order_id: ObjectId):
        return Order.document_repr_to_object(orders_collection.find_one({"_id": order_id}))

    @staticmethod
    def save(order: Order):
        order_save = Order(
            _id=order.id if order.id is not None else ObjectId(),
            order_date=order.order_date,
            subtotal=order.subtotal,
            shipping_cost=order.shipping_cost,
            shipping_address=order.shipping_address,
            cupon_discount=order.cupon_discount,
            total=order.total,
            items=order.items,
            shipping_method=order.shipping_method
        )
        saved = Order.get_db_repr(order_save)
        return Order.document_repr_to_object(orders_collection.find_one_and_update(
            {"_id": order_save._id},
            {"$set": saved},
            upsert=True,
            return_document=ReturnDocument.AFTER
        ))

    @staticmethod
    def get_db_repr(order: Order, get_long_names: bool = False):
        res = {value: getattr(order, key) for key, value in Order.LONG_TO_SHORT.items()}
        res["ots"] = int(order.order_date.timestamp())
        res.setdefault("it", [])
        res["it"] = list(map(lambda order_item: OrderItem.get_db_repr(order_item, get_long_names), res["it"]))
        res["sa"] = sa_module.ShippingAddress.get_db_repr(order.shipping_address, get_long_names) if order.shipping_address is not None else None
        res['sm'] = order.shipping_method.value

        if get_long_names:
            res["_id"] = str(res["_id"])
            res = {order.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] if value in doc else None for key, value in Order.LONG_TO_SHORT.items()}
        args["order_date"] = datetime.datetime.fromtimestamp(int(doc["ots"]))
        args["items"] = list(map(lambda order_item: OrderItem.document_repr_to_object(order_item), doc.get("it", [])))
        args["shipping_address"] = sa_module.ShippingAddress.document_repr_to_object(doc["sa"], address_index=0) if doc.get('sa', None) is not None else None
        args['shipping_method'] = sm_module.ShippingMethod._value2member_map_[doc['sm']]

        return Order(**args)

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

    @property
    def id(self):
        return self._id
