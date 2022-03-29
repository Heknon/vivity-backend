from bson import ObjectId
from pymongo import ReturnDocument

import database.business.item.item as item_module

from database import DocumentObject, items_collection


class ItemMetrics(DocumentObject):
    LONG_TO_SHORT = {
        "views": "vws",
        "orders": "ods",
        "likes": 'lks'
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            views: int,
            orders: int,
            likes: int,
    ):
        self.item_id = item_id
        self.views = views
        self.orders = orders
        self.likes = likes

    def add_view(self):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update({"_id": self.item_id}, {"$inc", "mtc.vws"}, return_document=ReturnDocument.AFTER)
        )

    def add_order(self):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update({"_id": self.item_id}, {"$inc", "mtc.ods"}, return_document=ReturnDocument.AFTER)
        )

    def add_like(self):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update({"_id": self.item_id}, {"$inc", "mtc.lks"}, return_document=ReturnDocument.AFTER)
        )

    def remove_like(self):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update({"_id": self.item_id}, {"$inc", "mtc.lks"}, return_document=ReturnDocument.AFTER)
        )

    @staticmethod
    def get_db_repr(item_metrics, get_long_names: bool = False):
        res = {value: getattr(item_metrics, key) for key, value in ItemMetrics.LONG_TO_SHORT.items()}

        if get_long_names:
            res = {item_metrics.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in ItemMetrics.LONG_TO_SHORT.items()}
        args["item_id"] = kwargs["_id"]

        return ItemMetrics(**args)

    def __getstate__(self):
        return ItemMetrics.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def shorten_field_name(self, field_name):
        return ItemMetrics.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ItemMetrics.SHORT_TO_LONG.get(field_name, None)
