from __future__ import annotations

from enum import Enum
from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, Image, Color, businesses_collection
import database.business.business as business


class ModificationButtonDataType(Enum):
    Text = 0
    Color = 1
    Image = 2


class ModificationButtonSide(Enum):
    Left = 0
    Center = 1
    Right = 2


class ModificationButton(DocumentObject):
    LONG_TO_SHORT = {
        "name": "nm",
        "data": "dta",
        "data_type": "dt",
        "multi_select": "ms"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: ObjectId,
            item_id: ObjectId,
            side: ModificationButtonSide,
            name: str,
            data: List[str | Color | Image],
            data_type: ModificationButtonDataType,
            multi_select: bool
    ):
        self.business_id = business_id
        self.item_id = item_id
        self.side = side

        self.name = name
        self.data = data
        self.data_type = data_type
        self.multi_select = multi_select

        self.updatable_fields = {
            "name", "multi_select"
        }

        self.access_prefix = f"it.{self.item_id.binary.decode('cp437')}.isf.mod.{self.side.value}"

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$set": {f"{self.access_prefix}.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"{self.access_prefix}.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def add_data(self, data: str | Color | Image) -> business.Business:
        assert type(data) is str or type(data) is Color or type(data) is Image, f"Data passed must be 'Color', 'Image' or 'str', not {type(data)}!"
        translated_data = data

        if type(data) is Color:
            translated_data = Color.get_db_repr(data)
        elif type(data) is Image:
            translated_data = data.image_id

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$addToSet": {f"{self.access_prefix}.dta": translated_data}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_data(self, index: int) -> business.Business:
        businesses_collection.update_one({"_id": self.business_id}, {"$unset": {f"{self.access_prefix}.dta.{index}": 1}})

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id}, {"$pull": {f"{self.access_prefix}.dta": None}}, return_document=ReturnDocument.AFTER
            )
        )

    def set_data_type(self, data_type: ModificationButtonDataType):
        businesses_collection.update_one(
            {"_id": self.business_id}, {"$set": {f"{self.access_prefix}.dt": data_type.value}}
        )

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id}, {"$set": {f"{self.access_prefix}.dta", []}},
                return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(ModificationButton.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(mod: ModificationButton, get_long_names: bool = False):
        res = {value: getattr(mod, key) for key, value in ModificationButton.LONG_TO_SHORT.items()}

        data_type = mod.data_type
        res["data_type"] = data_type.value

        if data_type == ModificationButtonDataType.Color:
            res["data"] = list(map(lambda color_bytes: Color.get_db_repr(color_bytes), res.get("data", [])))
        elif data_type == ModificationButtonDataType.Image:
            res["data"] = list(map(lambda image: image.image_id, res.get("data", [])))

        if get_long_names:
            res = {mod.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in ModificationButton.LONG_TO_SHORT.items()}

        args["data_type"] = ModificationButtonDataType(args["data_type"])
        data_type = args["data_type"]

        if data_type == ModificationButtonDataType.Color:
            args["data"] = list(map(lambda color_bytes: Color.document_repr_to_object(color_bytes), args.get("data", [])))
        elif data_type == ModificationButtonDataType.Image:
            args["data"] = list(map(lambda image_id: Image(image_id), args.get("data", [])))

        args["business_id"] = kwargs["business_id"]
        args["item_id"] = kwargs["item_id"]
        args["side"] = kwargs["side"]

        return ModificationButton(**args)

    def shorten_field_name(self, field_name):
        return ModificationButton.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ModificationButton.SHORT_TO_LONG.get(field_name, None)
