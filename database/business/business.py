from __future__ import annotations

import base64
from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.business_metrics as metrics_mod
import database.business.category as category_module
import database.business.contact as contact_module
import database.business.item.item as item_module
from database import DocumentObject, businesses_collection, Location, Image, unapproved_businesses_collection


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
        "metrics": 'mtc',
        "orders": "ord",
        "approved": "app",
        "admin_note": "ant"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            _id: ObjectId,
            name: str,
            location: Location,
            items: List[ObjectId],
            orders: List[ObjectId],
            categories: List[category_module.Category],
            contact: contact_module.Contact,
            owner_id_card: Image,
            national_business_id: str,
            metrics: metrics_mod.BusinessMetrics,
            approved: bool,
            admin_note: str,
    ):
        self._id = _id
        self.name = name
        self.location = location
        self.items = items
        self.categories = categories
        self.contact = contact
        self.owner_id_card = owner_id_card
        self.national_business_id = national_business_id
        self.metrics = metrics
        self.orders = orders
        self.approved = approved
        self.admin_note = admin_note

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

    def add_order(self, order_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {f"ord": order_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def add_order_by_id(business_id: ObjectId, order_id: ObjectId) -> Business:
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": business_id},
                {"$addToSet": {f"ord": order_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_order(self, order_id: ObjectId) -> Business:
        """
        Removes order from business orders NOT from orders collection.
        :param order_id: item object id
        """
        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {f"ord": order_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def update_business(
            _id: ObjectId,
            location: Location,
            name: str,
            phone: str,
            email: str,
            instagram: str,
            twitter: str,
            facebook: str,
    ):
        setUpdate = {}
        updates = [(Business.LONG_TO_SHORT["location"], Location.get_db_repr(location) if location is not None else None),
                   (Business.LONG_TO_SHORT["name"], name),
                   ("cntc.ph", phone),
                   ("cntc.ml", email),
                   ("cntc.ig", instagram),
                   ("cntc.tw", twitter),
                   ("cntc.fb", facebook)]
        for (name, data) in updates:
            if data is not None:
                setUpdate[name] = data

        update = {}
        if len(setUpdate) > 0:
            update["$set"] = setUpdate

        return Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": _id},
                update,
                return_document=ReturnDocument.AFTER,
            )
        )

    def get_items(self) -> List[item_module.Item]:
        return item_module.Item.get_items(*self.items)

    @staticmethod
    def get_item(item_id: ObjectId) -> item_module.Item:
        return item_module.Item.get_item(item_id)

    @staticmethod
    def approve_business(business_id: ObjectId, note: str):
        doc = unapproved_businesses_collection.find_one({"_id": business_id})
        if doc is None:
            doc = businesses_collection.find_one_and_update({"_id": business_id}, {"$set": {"ant": note, "app": True}},
                                                            return_document=ReturnDocument.AFTER)
            if doc is None:
                return

            return Business.document_repr_to_object(doc)

        doc["ant"] = note
        doc["app"] = True
        businesses_collection.insert_one(doc)
        unapproved_businesses_collection.delete_one({"_id": business_id})
        return Business.document_repr_to_object(doc)

    @staticmethod
    def send_admin_note(business_id: ObjectId, note: str):
        doc = unapproved_businesses_collection.find_one_and_update({"_id": business_id}, {"$set": {"ant": note}},
                                                                   return_document=ReturnDocument.AFTER)
        if doc is None:
            doc = businesses_collection.find_one_and_update({"_id": business_id}, {"$set": {"ant": note}}, return_document=ReturnDocument.AFTER)
            if doc is None:
                return

        return Business.document_repr_to_object(doc)

    @staticmethod
    def move_business_to_unapproved(business_id: ObjectId, note: str):
        doc = businesses_collection.find_one({"_id": business_id})
        if doc is None:
            doc = unapproved_businesses_collection.find_one_and_update({"_id": business_id}, {"$set": {"ant": note, "app": False}},
                                                                       return_document=ReturnDocument.AFTER)
            if doc is None:
                return

            return Business.document_repr_to_object(doc)

        doc["ant"] = note
        doc['app'] = False
        unapproved_businesses_collection.insert_one(doc)
        businesses_collection.delete_one({"_id": business_id})
        return Business.document_repr_to_object(doc)

    @staticmethod
    def create_business(
            name: str,
            location: Location,
            email: str,
            phone: str,
            image_id_card: bytes,
            national_id_business_id: str,
    ) -> Business:
        _id = ObjectId()
        image_id: Image = Image.upload(image_id_card, folder_name="business_ids/")

        return Business.document_repr_to_object(unapproved_businesses_collection.find_one_and_replace(
            {"_id": _id},
            Business.get_db_repr(Business(
                _id=_id,
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
                national_business_id=national_id_business_id,
                metrics=metrics_mod.BusinessMetrics(
                    _id,
                    0,
                ),
                approved=False,
                orders=[],
                admin_note="",
            )),
            upsert=True,
            return_document=ReturnDocument.AFTER
        ))

    def __repr__(self):
        return jsonpickle.encode(Business.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_business_by_id(business_id: ObjectId) -> Business:
        doc = businesses_collection.find_one({"_id": business_id})
        if doc is None:
            doc = unapproved_businesses_collection.find_one({"_id": business_id})
        return Business.document_repr_to_object(
            doc
        )

    @staticmethod
    def exists_by_id(_id: ObjectId):
        return businesses_collection.count_documents({"_id": _id}, limit=1) == 1

    @staticmethod
    def get_db_repr(business: Business, get_long_names: bool = False):
        res = {value: getattr(business, key) for key, value in Business.LONG_TO_SHORT.items()}

        res["loc"] = Location.get_db_repr(res.get('loc'), get_long_names) if res.get('loc', None) is not None else None
        res["it"] = list(map(str, res.get("it", []))) if get_long_names else res.get("it", [])
        res["ord"] = list(map(str, res.get("ord", []))) if get_long_names else res.get("ord", [])
        res["cat"] = list(map(lambda category: category_module.Category.get_db_repr(category, get_long_names), res.get("cat", [])))
        res["cntc"] = contact_module.Contact.get_db_repr(res["cntc"], get_long_names)
        res["mtc"] = metrics_mod.BusinessMetrics.get_db_repr(res['mtc'], get_long_names)
        res['oic'] = res['oic'].image_id if type(res['oic']) == Image else res['oic']

        if get_long_names:
            res["_id"] = str(business._id)
            res = {business.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        if doc is None:
            return None

        args = {key: doc[value] for key, value in Business.LONG_TO_SHORT.items()}

        args["location"] = Location.document_repr_to_object(args.get('location')) if args.get('location') is not None else None
        args["items"] = args.get("items", [])
        args["categories"] = \
            list(map(lambda category_doc: category_module.Category.document_repr_to_object(category_doc, business_id=args["_id"]),
                     args.get("categories", [])))

        args["contact"] = contact_module.Contact.document_repr_to_object(args["contact"], business_id=args["_id"]) \
            if args.get("contact", None) is not None else None

        args["metrics"] \
            = metrics_mod.BusinessMetrics.document_repr_to_object(args['metrics'], business_id=args["_id"]) if args.get('mtc', None) is not None \
            else metrics_mod.BusinessMetrics(args["_id"], 0)

        args["owner_id_card"] = Image(args.get("owner_id_card", None))

        return Business(**args)

    def shorten_field_name(self, field_name):
        return Business.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Business.SHORT_TO_LONG.get(field_name, None)

    def __getstate__(self):
        res = Business.get_db_repr(self, True)
        return res

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def id(self):
        return self._id
