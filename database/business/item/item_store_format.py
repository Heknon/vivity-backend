from __future__ import annotations

from typing import List, Dict

from bson import ObjectId
from pymongo import ReturnDocument

from database import DocumentObject, businesses_collection
import database.business.business as business
import database.business.item.modification_button as mod_module


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
            business_id: ObjectId,
            item_id: ObjectId,
            title: str,
            subtitle: str,
            description: str,
            modification_buttons: Dict[mod_module.ModificationButtonSide, mod_module.ModificationButton]
    ):
        self.business_id = business_id
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

    def update_field(self, field_name, value) -> business.Business:
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": ObjectId(self.business_id)},
                {"$set": {f"it.{self.item_id.binary.decode('cp437')}.isf.{field_name}": value}},
                return_document=ReturnDocument.AFTER
            )
        )

    def update_fields(self, **kwargs) -> business.Business:
        filtered_kwargs = filter(lambda name, value: name in self.updatable_fields, kwargs.items())
        update_dict = {
            f"it.{self.item_id.binary.decode('cp437')}.isf.{self.shorten_field_name(key)}": value for key, value in filtered_kwargs
        }

        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": ObjectId(self.business_id)}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
            )
        )

    def set_modification_button(self, side: mod_module.ModificationButtonSide, modification_button: mod_module.ModificationButton):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$set": {f"it.{self.item_id.binary.decode('cp437')}.isf.mod.{side.value}": mod_module.ModificationButton.get_db_repr(modification_button)}},
                return_document=ReturnDocument.AFTER
            )
        )

    def unset_modification_button(self, side: mod_module.ModificationButtonSide):
        return business.Business.document_repr_to_object(
            businesses_collection.find_one_and_update(
                {"_id": self.business_id},
                {"$unset": {f"it.{self.item_id.binary.decode('cp437')}.isf.mod.{side.value}": 1}},
                return_document=ReturnDocument.AFTER
            )
        )

    @staticmethod
    def get_db_repr(isf: ItemStoreFormat) -> dict:
        res = {value: getattr(isf, key) for key, value in ItemStoreFormat.LONG_TO_SHORT.items()}
        res["mod"] = list(map(lambda mod: mod_module.ModificationButton.get_db_repr(mod), res.get("mod", [])))

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in ItemStoreFormat.LONG_TO_SHORT.items()}
        args["modification_buttons"] = \
            list(map(lambda side_num, mod_doc: mod_module.ModificationButton.document_repr_to_object(
                mod_doc, business_id=kwargs["business_id"], item_id=kwargs["item_id"], side=side_num
            ), args.get("modification_buttons", {}).items()))

        args["business_id"] = kwargs["business_id"]
        args["item_id"] = kwargs["item_id"]

        return ItemStoreFormat(**args)

    def shorten_field_name(self, field_name):
        return ItemStoreFormat.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return ItemStoreFormat.SHORT_TO_LONG.get(field_name, None)
