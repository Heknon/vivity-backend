from __future__ import annotations

from enum import Enum
from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.item as item_module
from database import DocumentObject, Image, Color, items_collection


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
        "multi_select": "ms",
        "side": "sd"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            side: ModificationButtonSide,
            name: str,
            data: List[str | Color | Image],
            data_type: ModificationButtonDataType,
            multi_select: bool
    ):
        self.item_id = item_id
        self.side = side

        self.name = name
        self.data = data
        self.data_type = data_type
        self.multi_select = multi_select

        self.updatable_fields = {
            "name", "multi_select", "side"
        }

        self.access_prefix = f"isf.mod.{self.side.value}"

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> item_module.Item:
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id},
                {"$set": {f"{self.access_prefix}.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> item_module.Item:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"{self.access_prefix}.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def add_data(self, data: str | Color | Image) -> item_module.Item:
        assert type(data) is str or type(data) is Color or type(data) is Image, f"Data passed must be 'Color', 'Image' or 'str', not {type(data)}!"
        translated_data = data

        if type(data) is Color:
            translated_data = Color.get_db_repr(data)
        elif type(data) is Image:
            translated_data = data.image_id

        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id},
                {"$addToSet": {f"{self.access_prefix}.dta": translated_data}},
                return_document=ReturnDocument.AFTER
            )
        )

    def remove_data(self, index: int) -> item_module.Item:
        items_collection.update_one({"_id": self.item_id}, {"$unset": {f"{self.access_prefix}.dta.{index}": 1}})

        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id}, {"$pull": {f"{self.access_prefix}.dta": None}}, return_document=ReturnDocument.AFTER
            )
        )

    def set_data_type(self, data_type: ModificationButtonDataType):
        items_collection.update_one(
            {"_id": self.item_id}, {"$set": {f"{self.access_prefix}.dt": data_type.value}}
        )

        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id}, {"$set": {f"{self.access_prefix}.dta", []}},
                return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(ModificationButton.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(mod: ModificationButton, get_long_names: bool = False):
        res = {value: getattr(mod, key) for key, value in ModificationButton.LONG_TO_SHORT.items()}

        data_type = mod.data_type
        res["dt"] = data_type.value
        res['nm'] = mod.name.strip()

        if data_type == ModificationButtonDataType.Color:
            res["dta"] = list(map(lambda color_hex: int(color_hex.hexColor), res.get("dta", [])))
        elif data_type == ModificationButtonDataType.Image:
            res["dta"] = list(map(lambda image: image.image_id, res.get("dta", [])))
        elif data_type == ModificationButtonDataType.Text:
            res["dta"] = list(map(lambda text: text.strip(), res.get("dta", [])))

        res["sd"] = res["sd"].value

        if get_long_names:
            res = {mod.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, use_long_name=False, **kwargs):
        args = {key: doc[value if not use_long_name else key] for key, value in ModificationButton.LONG_TO_SHORT.items()}

        args["data_type"] = ModificationButtonDataType(args["data_type"])
        data_type = args["data_type"]
        args['name'] = args['name'].strip()

        if data_type == ModificationButtonDataType.Color:
            args["data"] = list(map(lambda color_hex: Color.document_repr_to_object(color_hex), args.get("data", [])))
        elif data_type == ModificationButtonDataType.Image:
            args["data"] = list(map(lambda image_id: Image(image_id), args.get("data", [])))
        elif data_type == ModificationButtonDataType.Text:
            args["data"] = list(map(lambda text: text.strip(), args.get("data", [])))

        args["side"] = ModificationButtonSide._value2member_map_[args["side"]]
        args["item_id"] = kwargs["item_id"]

        return ModificationButton(**args)

    def shorten_field_name(self, field_name):
        return ModificationButton.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ModificationButton.SHORT_TO_LONG.get(field_name, None)
