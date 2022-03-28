from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.category as category_module
import database.business.contact as contact_module
import database.business.item.item as item_module
from database import DocumentObject, businesses_collection, Location, Image

# TODO: Add option to switch location of business- should switch all items as well.
class Business(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "name": "nm",
        "location": "loc",
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
            location: Location,
            items: List[ObjectId],
            categories: List[category_module.Category],
            contact: contact_module.Contact,
            owner_id_card: Image,
            national_business_id: str,
    ):
        self._id = _id
        self.rating = rating
        self.name = name
        self.location = location
        self.items = items
        self.categories = categories
        self.contact = contact
        self.owner_id_card = owner_id_card
        self.national_business_id = national_business_id

        self.updatable_fields = {
            "name", "national_business_id", "owner_id_card", "contact", "location"
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
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
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

    def get_categories_with_items(self):
        categories = dict()
        items: dict = {item.id: item for item in self.get_items()}

        for category in self.categories:
            categories[category.name] = []

            for item_id in category.items_ids:
                categories[category.name].append(items[item_id])

    def get_category_by_name(self, name: str, get_items: bool) -> category_module.Category:
        category: category_module.Category = category_module.Category.document_repr_to_object(
            businesses_collection.find_one(
                {"_id": self._id, "cat": {"$elemMatch": {"name": name}}}, {"cat.$": 1, "_id": 0}
            )["cat"][0]
        )

        if get_items:
            category.items = item_module.Item.get_items(*category.items_ids)

        return category

    def add_item(self, item_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {f"it": item_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_item(self, item_id: ObjectId) -> Business:
        """
        Removes item from business items NOT from items collection.
        :param item_id: item object id
        """
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {f"it": item_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def get_items(self) -> List[item_module.Item]:
        return item_module.Item.get_items(*self.items)

    @staticmethod
    def get_item(item_id: ObjectId) -> item_module.Item:
        return item_module.Item.get_item(item_id)

    @staticmethod
    def create_business(
            name: str,
            location: Location,
            email: str,
            phone: str,
            image_id_card: bytes,
            national_id_business_id: str

    ) -> Business:
        _id = ObjectId()
        image_id: Image = Image.upload(image_id_card, folder_name="business_ids/")

        return Business.document_repr_to_object(businesses_collection.find_one_and_replace(
            {"_id": _id},
            Business.get_db_repr(Business(
                _id=_id,
                rating=0,
                name=name,
                location=location,
                items=[],
                categories=[],
                contact=contact_module.Contact(
                    business_id=_id,
                    phone=phone,
                    email=email,
                    instagram=None,
                    twitter=None,
                    facebook=None
                ),
                owner_id_card=image_id,
                national_business_id=national_id_business_id
            )),
            upsert=True,
            return_document=ReturnDocument.AFTER
        ))

    def __repr__(self):
        return jsonpickle.encode(Business.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_business_by_id(business_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one({"_id": business_id})
        )

    @staticmethod
    def exists_by_id(_id: ObjectId):
        return businesses_collection.count_documents({"_id": _id}, limit=1) == 1

    @staticmethod
    def get_db_repr(business: Business, get_long_names: bool = False):
        res = {value: getattr(business, key) for key, value in Business.LONG_TO_SHORT.items()}

        res["loc"] = Location.get_db_repr(res.get('loc'), get_long_names) if res.get('loc', None) is not None else None
        res["it"] = res.get("it", [])
        res["cat"] = list(map(lambda category: category_module.Category.get_db_repr(category, get_long_names), res.get("cat", [])))
        res["cntc"] = contact_module.Contact.get_db_repr(res["cntc"], get_long_names)
        res["oic"] = res["oic"].__getstate__()

        if get_long_names:
            res = {business.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Business.LONG_TO_SHORT.items()}

        rating = sum(map(lambda item: item.calculate_rating(), args.get("items", [])))
        args["rating"] = rating
        args["location"] = Location.document_repr_to_object(args.get('location')) if args.get('location') is not None else None
        args["items"] = args.get("items", [])
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

    def __getstate__(self):
        res = Business.get_db_repr(self, True)
        res["_id"] = str(self._id)
        return res

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def id(self):
        return self._id
