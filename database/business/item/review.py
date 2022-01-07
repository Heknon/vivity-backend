from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId

from database import DocumentObject, Image


class Review(DocumentObject):
    LONG_TO_SHORT = {
        "poster_id": "pid",
        "pfp_image": "pfp",
        "poster_name": "nme",
        "rating": "rtn",
        "text_content": "txt",
        "images": "imgs"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            poster_id: ObjectId,
            pfp_image: Image,
            poster_name: str,
            rating: float,
            text_content: str,
            images: List[Image]
    ):
        self.poster_id = poster_id
        self.pfp_image = pfp_image
        self.poster_name = poster_name
        self.rating = rating
        self.text_content = text_content
        self.images = images

    def __repr__(self):
        return jsonpickle.encode(Review.get_db_repr(self), unpicklable=False)

    @staticmethod
    def get_db_repr(review: Review):
        res = {value: getattr(review, key) for key, value in Review.LONG_TO_SHORT.items()}
        res["pfp"] = res["pfp"].image_id
        res["imgs"] = list(map(lambda img: img.image_id, res.get("imgs", [])))

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in Review.LONG_TO_SHORT.items()}

        args["pfp_image"] = Image(args.get("pfp_image", None))
        args["images"] = list(map(lambda image_id: Image(image_id), args.get("images", [])))

        return Review(**args)

    def shorten_field_name(self, field_name):
        return Review.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return Review.SHORT_TO_LONG.get(field_name, None)
