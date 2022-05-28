from __future__ import annotations

from typing import List

import jsonpickle
from bson import ObjectId
from pymongo import ReturnDocument

import database.business.business as business
import database.business.item.item as item_module
import database.business.item.modification_button as mod_module
from database import DocumentObject, items_collection


class ItemStoreFormat(DocumentObject):
    LONG_TO_SHORT = {
        "title": "ttl",
        "subtitle": "stl",
        "description": "dsc",
        "modification_buttons": "mod"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            item_id: ObjectId,
            title: str,
            subtitle: str,
            description: str,
            modification_buttons: List[mod_module.ModificationButton]
    ):
        self.item_id = item_id
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.modification_buttons = modification_buttons

        self.updatable_fields = {
            "title", "subtitle", "description"
        }

    def generate_update_methods(self):
        for field_name in self.updatable_fields:
            method_name = "update_" + field_name
            setattr(self, method_name, lambda value: self.update_field(self.shorten_field_name(field_name), value))

    def update_field(self, field_name, value) -> item_module.Item:
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id},
                {"$set": {f"isf.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda item: item[0] in self.updatable_fields, kwargs.items())
        update_dict = {
            f"isf.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def set_modification_button(self, side: mod_module.ModificationButtonSide, modification_button: mod_module.ModificationButton):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id},
                {"$set": {f"isf.mod.{side.value}": mod_module.ModificationButton.get_db_repr(modification_button)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def unset_modification_button(self, side: mod_module.ModificationButtonSide):
        return item_module.Item.document_repr_to_object(
            items_collection.find_one_and_update(
                {"_id": self.item_id},
                {"$unset": {f"isf.mod.{side.value}": 1}},
                return_document=ReturnDocument.AFTER
            )
        )

    def __repr__(self):
        return jsonpickle.encode(ItemStoreFormat.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(isf: ItemStoreFormat, get_long_names: bool = False) -> dict:
        res = {value: getattr(isf, key) for key, value in ItemStoreFormat.LONG_TO_SHORT.items()}
        res["mod"] = list(
            map(lambda mod: mod_module.ModificationButton.get_db_repr(mod, get_long_names) if mod is not None else None, res.get("mod", [])))
        res["mod"] = list(filter(lambda mod: mod is not None, res['mod']))

        if get_long_names:
            res = {isf.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in ItemStoreFormat.LONG_TO_SHORT.items()}
        args["modification_buttons"] = \
            list(map(lambda mod_doc: mod_module.ModificationButton.document_repr_to_object(
                mod_doc, item_id=kwargs["item_id"]
            ) if mod_doc is not None else None, args.get("modification_buttons", [])))

        args['modification_buttons'] = list(filter(lambda mod: mod is not None, args['modification_buttons']))

        args["item_id"] = kwargs["item_id"]

        return ItemStoreFormat(**args)

    def shorten_field_name(self, field_name):
        return ItemStoreFormat.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ItemStoreFormat.SHORT_TO_LONG.get(field_name, None)

    def __getstate__(self):
        return ItemStoreFormat.get_db_repr(self, True)

    def __setstate__(self, state):
        self.__dict__.update(state)
