from __future__ import annotations

from typing import List, Dict

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import Image, DocumentObject, businesses_collection
import database.business.business as business

import database.business.item.item_store_format as isf_module
import database.business.item.review as review_module


class Item(DocumentObject):
    LONG_TO_SHORT = {
        "price": "p",
        "images": "im",
        "preview_image": "pi",
        "reviews": "rs",
        "item_store_format": "isf",
        "brand": "br",
        "category": "cat",
        "tags": "tg",
        "stock": "stk",
        "_id": "_id"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            price: float,
            images: List[Image],
            preview_image: int,
            reviews: Dict[ObjectId, review_module.Review],
            item_store_format: isf_module.ItemStoreFormat,
            brand: str,
            category: str,
            tags: List[str],
            stock: int,
            _id: ObjectId = ObjectId(),
    ):
        self.business_id = business_id
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
        self.rating = -1

        self.updatable_fields = {
            "price", "preview_image", "brand", "category", "stock"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": ObjectId(self._id)},
                {"$set": {f"it.{self._id.binary.decode('cp437')}.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"it.{self._id.binary.decode('cp437')}.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": ObjectId(self.business_id)}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def add_tags(self, *tags: str) -> business.Business:
        lowered_tags = list(map(lambda tag: tag.lower(), tags))

        return business.Business.document_repr_to_object(businesses_collection.find_one_and_update(
            {"_id": self.business_id},
            {"$addToSet": {f"it.{self._id.binary.decode('cp437')}.tg": {"$each": lowered_tags}}},
            return_document=ReturnDocument.AFTER
        ))

    def remove_tags(self, *tags: str) -> business.Business:
        lowered_tags = list(map(lambda tag: tag.lower(), tags))

        return business.Business.document_repr_to_object(businesses_collection.find_one_and_update(
            {"_id": self.business_id},
            {"$pullAll": {"it." + self._id.binary.decode("cp437"): lowered_tags}},
            return_document=ReturnDocument.AFTER
        ))

    def add_image(self, image: Image) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$addToSet": {f"it.{self._id.binary.decode('cp437')}.im": image.image_id}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_image(self, index: int) -> business.Business:
        businesses_collection.update_one({"_id": self.business_id}, {"$unset": {f"it.{self._id.binary.decode('cp437')}.im.{index}": 1}})

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update({"_id": self.business_id}, {"$pull": {"it": None}}, return_document=ReturnDocument.AFTER)
        )

    def add_review(self, review: review_module.Review) -> business.Business:
        self.rating = -1
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$set": {f"it.{self._id.binary.decode('cp437')}.rs.{review.poster_id.binary.decode('cp437')}": review_module.Review.get_db_repr(review)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_review(self, poster_id: ObjectId) -> business.Business:
        self.rating = -1
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$unset": {f"it.{self._id.binary.decode('cp437')}.rs.{poster_id.binary.decode('cp437')}": 1}},
                return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(Item.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(item: Item, get_long_names: bool = False):
        res = {value: getattr(item, key) for key, value in Item.LONG_TO_SHORT.items()}

        res["pi"] = res["pi"].image_id if res.get("pi", None) is not None else None
        res["isf"] = isf_module.ItemStoreFormat.get_db_repr(res["isf"])

        res["im"] = list(map(lambda image: image.image_id, res["im"]))
        res["rs"] = list(map(lambda review: review_module.Review.get_db_repr(review), res.get("rs", [])))

        if get_long_names:
            res = {item.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Item.LONG_TO_SHORT.items()}
        business_id = kwargs["business_id"]

        args["preview_image"] = Image(args["preview_image"])
        args["item_store_format"] = \
            isf_module.ItemStoreFormat.document_repr_to_object(args["item_store_format"], business_id=business_id, item_id=args["_id"])

        args["images"] = list(map(lambda image_id: Image(image_id), args["images"]))
        args["reviews"] = list(map(lambda review_doc: review_module.Review.document_repr_to_object(review_doc), args["reviews"]))
        args["business_id"] = business_id

        return Item(**args)

    def calculate_rating(self) -> float:
        if self.rating == -1:
            self.rating = sum(map(lambda review: review.rating, self.reviews)) / float(len(self.reviews))
        return self.rating

    def shorten_field_name(self, field_name):
        return Item.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Item.SHORT_TO_LONG.get(field_name, None)
