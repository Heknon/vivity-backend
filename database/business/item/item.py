from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.item.item_store_format as isf_module
import database.business.item.review as review_module
import database.business.item.item_metrics as metrics_mod
from database import Image, DocumentObject, items_collection, Location


class Item(DocumentObject):
    LONG_TO_SHORT = {
        "_id": "_id",
        "business_id": "bid",
        "business_name": "bnm",
        "price": "p",
        "images": "im",
        "preview_image": "pi",
        "reviews": "rs",
        "item_store_format": "isf",
        "brand": "br",
        "category": "cat",
        "tags": "tg",
        "stock": "stk",
        "location": "loc",
        "metrics": "mtc",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            business_name: str,
            price: float,
            images: List[Image],
            preview_image: int,
            reviews: List[review_module.Review],
            item_store_format: isf_module.ItemStoreFormat,
            brand: str,
            category: str,
            tags: List[str],
            stock: int,
            location: Location,
            metrics: metrics_mod.ItemMetrics,
            _id: ObjectId = ObjectId(),
    ):
        self.business_id = business_id
        self.business_name = business_name
        self._id = _id
        self.price = price
        self.images = images
        self.preview_image = preview_image
        self.reviews = reviews
        self.item_store_format = item_store_format
        self.brand = brand
        self.category = category
        self.tags = tags
        self.stock = stock
        self.location = location
        self.metrics = metrics
        self.should_recalculate_rating = True

        self.updatable_fields = {
            "price", "preview_image", "brand", "category", "stock"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> Item:
        return Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self._id},
                {"$set": {field_name: value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def add_tags(self, *tags: str) -> Item:
        lowered_tags = list(map(lambda tag: tag.lower(), tags))

        return Item.document_repr_to_object(items_collection.find_one_and_update(
            {"_id": self._id},
            {"$addToSet": {"tg": {"$each": lowered_tags}}},
            return_document=ReturnDocument.AFTER
        ))

    def remove_tags(self, *tags: str) -> Item:
        lowered_tags = list(map(lambda tag: tag.lower(), tags))

        return Item.document_repr_to_object(items_collection.find_one_and_update(
            {"_id": self._id},
            {"$pullAll": {"tg": lowered_tags}},
            return_document=ReturnDocument.AFTER
        ))

    def add_image(self, image: Image) -> Item:
        return Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {f"im": image.image_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_image(self, index: int) -> Item:
        items_collection.update_one({"_id": self._id}, {"$unset": {f"im.{index}": 1}})

        return Item.document_repr_to_object(
            items_collection.find_one_and_update({"_id": self._id}, {"$pull": {"im": None}}, return_document=ReturnDocument.AFTER)
        )

    def add_review(self, review: review_module.Review) -> Item:
        self.should_recalculate_rating = True
        return Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self._id},
                {"$addToSet": {f"rs": review_module.Review.get_db_repr(review)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_review(self, poster_id: ObjectId) -> Item:
        self.should_recalculate_rating = True
        return Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self._id},
                {"$pull": {f"rs.$.pid": poster_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_tags(self, added: List[str], removed: List[str]):
        lowered_added_tags = list(map(lambda tag: tag.lower(), added))
        lowered_removed_tags = list(map(lambda tag: tag.lower(), removed))

        return Item.document_repr_to_object(items_collection.find_one_and_update(
            {"_id": self._id},
            {"$pullAll": {"tg": lowered_removed_tags}, "$addToSet": {"tg": {"$each": lowered_added_tags}}},
            return_document=ReturnDocument.AFTER
        ))

    def add_view(self):
        return Item.document_repr_to_object(items_collection.find_one_and_update(
            {"_id": self._id},
            {"$inc": "vws"},
            return_document=ReturnDocument.AFTER
        ))

    def update_fields(
            self,
            title: str,
            subtitle: str,
            description: str,
            price: float,
            brand: str,
            category: str,
            stock: int,
            added_tags: List[str],
            removed_tags: List[str],
            add_image: str,

    ):
        lowered_added_tags = list(map(lambda tag: tag.lower(), added_tags))
        lowered_removed_tags = list(map(lambda tag: tag.lower(), removed_tags))

        return Item.document_repr_to_object(items_collection.find_one_and_update(
            {"_id": self._id},
            {
                "$set": {
                    "isf.ttl": title if title is not None else self.item_store_format.title,
                    "isf.stl": subtitle if subtitle is not None else self.item_store_format.subtitle,
                    "isf.dsc": description if description is not None else self.item_store_format.description,
                    "p": price if price is not None else self.price,
                    "br": brand if brand is not None else self.brand,
                    "cat": category if category is not None else self.category,
                    "stk": stock if stock is not None else self.stock
                },
                "$pullAll": {
                    "tg": lowered_removed_tags
                } if len(lowered_removed_tags) > 0 else {},
                "$addToSet": {
                    "tg": {"$each": lowered_added_tags} if len(lowered_added_tags) > 0 else {"$each": []},
                    "im": add_image
                },
            },
            upsert=False,
            return_document=ReturnDocument.AFTER
        ))

    @staticmethod
    def delete_item(item_id: ObjectId):
        items_collection.delete_one({"_id": item_id})

    def __repr__(self):
        return jsonpickle.encode(Item.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(item: Item, get_long_names: bool = False):
        res = {value: getattr(item, key) for key, value in Item.LONG_TO_SHORT.items()}

        res["pi"] = res["pi"].image_id if res.get("pi", None) is not None else None
        res["isf"] = isf_module.ItemStoreFormat.get_db_repr(res["isf"], get_long_names)

        res["im"] = list(map(lambda image: image.image_id, res["im"]))
        res["rs"] = list(map(lambda review: review_module.Review.get_db_repr(review, get_long_names), res.get("rs", [])))
        res['loc'] = Location.get_db_repr(res['loc'], get_long_names)
        res["mtc"] = metrics_mod.ItemMetrics.get_db_repr(res['mtc'], get_long_names)

        if get_long_names:
            res["bid"] = str(res["bid"])
            res["_id"] = str(res["_id"])
            res = {item.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Item.LONG_TO_SHORT.items()}

        args["preview_image"] = Image(args["preview_image"])
        args["item_store_format"] = \
            isf_module.ItemStoreFormat.document_repr_to_object(args["item_store_format"], business_id=args["business_id"], item_id=args["_id"])

        args["images"] = list(map(lambda image_id: Image(image_id), args["images"]))
        args["reviews"] = list(map(lambda review_doc: review_module.Review.document_repr_to_object(review_doc), args["reviews"]))
        args["business_id"] = args["business_id"]
        args['location'] = Location.document_repr_to_object(args['location'])
        args['metrics'] \
            = metrics_mod.ItemMetrics.document_repr_to_object(args['metrics'], _id=doc["_id"]) if args.get("metrics", None) is not None \
            else metrics_mod.ItemMetrics(doc["_id"], 0, 0, 0)

        return Item(**args)

    @staticmethod
    def get_items(*item_ids: ObjectId) -> List[Item]:
        return list(map(
            lambda doc: Item.document_repr_to_object(doc),
            items_collection.find(
                {"_id": {"$in": item_ids}}
            )
        ))

    @staticmethod
    def get_item(item_id: ObjectId) -> Item:
        return Item.document_repr_to_object(
            items_collection.find_one({"_id": item_id})
        )

    @staticmethod
    def save_item(
            business_id: ObjectId,
            business_name: str,
            price: float,
            images: List[Image],
            preview_image: int,
            reviews: List[review_module.Review],
            item_store_format: isf_module.ItemStoreFormat,
            brand: str,
            category: str,
            tags: List[str],
            stock: int,
            location: Location,
            metrics: metrics_mod.ItemMetrics
    ) -> Item:
        _id = ObjectId()

        return Item.document_repr_to_object(items_collection.find_one_and_replace(
            {"_id": _id},
            Item.get_db_repr(Item(
                business_id=business_id,
                business_name=business_name,
                price=price,
                images=images,
                preview_image=preview_image,
                reviews=reviews,
                item_store_format=isf_module.ItemStoreFormat(
                    item_id=_id,
                    title=item_store_format.title,
                    subtitle=item_store_format.subtitle,
                    description=item_store_format.description,
                    modification_buttons=item_store_format.modification_buttons,
                ),
                brand=brand,
                category=category,
                tags=tags,
                stock=stock,
                location=location,
                _id=_id,
                metrics=metrics
            )),
            upsert=True,
            return_document=ReturnDocument.AFTER
        ))

    def calculate_rating(self) -> float:
        if self.should_recalculate_rating:
            self.should_recalculate_rating = sum(map(lambda review: review.should_recalculate_rating, self.reviews)) / float(len(self.reviews))
        return self.should_recalculate_rating

    def shorten_field_name(self, field_name):
        return Item.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Item.SHORT_TO_LONG.get(field_name, None)

    @property
    def id(self):
        return self._id

    def __getstate__(self):
        return Item.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
