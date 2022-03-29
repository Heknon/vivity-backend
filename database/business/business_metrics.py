from bson import ObjectId
from pymongo import ReturnDocument

import database.business.business as business_module

from database import DocumentObject, businesses_collection


class BusinessMetrics(DocumentObject):
    LONG_TO_SHORT = {
        "views": "vws",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            views: int,
    ):
        self.business_id = business_id
        self.views = views

    def add_like(self):
        return business_module.Business.document_repr_to_object(
            businesses_collection.find_one_and_update({"_id": self.business_id}, {"$inc", "mtc.vws"}, return_document=ReturnDocument.AFTER)
        )

    @staticmethod
    def get_db_repr(item_metrics, get_long_names: bool = False):
        res = {value: getattr(item_metrics, key) for key, value in BusinessMetrics.LONG_TO_SHORT.items()}

        if get_long_names:
            res = {item_metrics.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in BusinessMetrics.LONG_TO_SHORT.items()}
        args["business_id"] = kwargs["_id"]

        return BusinessMetrics(**args)

    def __getstate__(self):
        return BusinessMetrics.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def shorten_field_name(self, field_name):
        return BusinessMetrics.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return BusinessMetrics.SHORT_TO_LONG.get(field_name, None)
