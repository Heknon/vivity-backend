from __future__ import annotations

from typing import List, Dict

from bson import ObjectId
from pymongo import ReturnDocument

import database.business.category as category_module
import database.business.contact as contact_module
import database.business.item.item as item_module
from database import DocumentObject, businesses_collection, Location, Image


class Business(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "name": "nm",
        "locations": "loc",
        "items": "it",
        "categories": "cat",
        "contact": "cntc",
        "owner_id_card": "oic",
        "national_business_id": "nbi",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            rating: float,
            name: str,
            locations: List[Location],
            items: Dict[ObjectId, item_module.Item],
            categories: List[category_module.Category],
            contact: contact_module.Contact,
            owner_id_card: Image,
            national_business_id: str,
    ):
        self._id = _id
        self.rating = rating
        self.name = name
        self.locations = locations
        self.items = items
        self.categories = categories
        self.contact = contact
        self.owner_id_card = owner_id_card
        self.national_business_id = national_business_id

        self.updatable_fields = {
            "name", "national_business_id", "owner_id_card"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$set": {field_name: value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> Business:
        filtered_kwargs = filter(lambda name, value: name in self.updatable_fields, kwargs.items())
        update_dict = {
            self.shorten_field_name(key): value for key, value in filtered_kwargs
        }

        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def add_category(self, category: category_module.Category) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {"cat": category_module.Category.get_db_repr(category)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_category(self, name: str) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {"cat": {"$elemMatch": {"name": name}}}},
                return_document=ReturnDocument.AFTER
            )
        )

    def get_categories(self) -> List[category_module.Category]:
        return list(
            map(
                lambda category_doc: category_module.Category.document_repr_to_object(category_doc),
                businesses_collection.find_one({"_id": self._id}, {"cat": 1, "_id": 0})["cat"]
            )
        )

    def get_category_by_name(self, name: str) -> category_module.Category:
        return category_module.Category.document_repr_to_object(
            businesses_collection.find_one(
                {"_id": self._id, "cat": {"$elemMatch": {"name": name}}}, {"cat.$": 1, "_id": 0}
            )["cat"][0]
        )

    def add_item(self, item: item_module.Item) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$set": {f"it.{item._id.binary.decode('cp437')}": item_module.Item.get_db_repr(item)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_item(self, item_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$unset": {f"it.{item_id.binary.decode('cp437')}": 1}},
                return_document=ReturnDocument.AFTER
            )
        )

    def get_items(self, *item_ids: ObjectId) -> List[item_module.Item]:
        if item_ids is None or len(item_ids) == 0:
            return list(map(
                lambda doc: item_module.Item.document_repr_to_object(doc),
                businesses_collection.find({"_id": self._id}, {f"it": 1, "_id": 0})
            ))

        accepts = {f"it.{item_id.binary.decode('cp437')}": 1 for item_id in item_ids}
        accepts["_id"] = 0

        return list(map(
            lambda doc: item_module.Item.document_repr_to_object(doc),
            businesses_collection.find_one({"_id": self._id}, **accepts)["it"].values()
        ))

    def get_item(self, item_id: ObjectId) -> item_module.Item:
        return item_module.Item.document_repr_to_object(
            businesses_collection.find_one({"_id": self._id}, {f"it.{item_id.binary.decode('cp437')}": 1, "_id": 0})["it"].values()[0]
        )

    def add_location(self, location: Location) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {"loc": Location.get_db_repr(location)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_location(self, location: Location) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {"loc": {"$elemMatch": Location.get_db_repr(location)}}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_business_by_id(business_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one({"_id": business_id})
        )

    @staticmethod
    def get_db_repr(business: Business):
        res = {value: getattr(business, key) for key, value in item_module.Item.LONG_TO_SHORT.items()}

        res["loc"] = list(map(lambda loc: Location.get_db_repr(loc), res.get("loc", [])))
        res["it"] = list(map(lambda item: item_module.Item.get_db_repr(item), res.get("it", [])))
        res["cat"] = list(map(lambda category: category_module.Category.get_db_repr(category), res.get("cat", [])))
        res["cntc"] = contact_module.Contact.get_db_repr(res["cntc"])
        res["oic"] = res["oic"].image_id

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in item_module.Item.LONG_TO_SHORT.items()}

        rating = sum(map(lambda item: item.calculate_rating(), args.get("items", [])))
        args["rating"] = rating
        args["locations"] = list(map(lambda loc_doc: Location.document_repr_to_object(loc_doc), args.get("locations", [])))
        args["items"] = list(map(lambda item_doc: item_module.Item.document_repr_to_object(item_doc, business_id=args["_id"]), args.get("items", [])))
        args["categories"] = \
            list(map(lambda category_doc: category_module.Category.document_repr_to_object(category_doc, business_id=args["_id"]),
                     args.get("categories", [])))
        args["contact"] = contact_module.Contact.document_repr_to_object(args["contact"], business_id=args["_id"]) if args.get("contact",
                                                                                                                               None) is not None else None
        args["owner_id_card"] = Image(args.get("owner_id_card", None))

        return Business(**args)

    def shorten_field_name(self, field_name):
        return Business.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Business.SHORT_TO_LONG.get(field_name, None)
