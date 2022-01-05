from __future__ import annotations

from typing import List

from database import DocumentObject, Image
from database.business.item import SelectedModificationButton


class OrderItem(DocumentObject):
    LONG_TO_SHORT = {
        "business_id": "bid",
        "item_id": "iid",
        "preview_image": "pi",
        "title": "ttl",
        "subtitle": "sbt",
        "description": "dsc",
        "selected_modification_button_data": "smb",
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(
            self,
            business_id: bytes,
            item_id: int,
            preview_image: Image,
            title: str,
            subtitle: str,
            description: str,
            selected_modification_button_data: List[SelectedModificationButton]
    ):
        self.business_id = business_id
        self.item_id = item_id
        self.preview_image = preview_image
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.selected_modification_button_data = selected_modification_button_data

    @staticmethod
    def get_db_repr(
            order_item: OrderItem
    ) -> dict:
        res = {value: getattr(order_item, key) for key, value in OrderItem.LONG_TO_SHORT.items()}
        res.setdefault("smb", [])
        res["smb"] = list(map(lambda smb: SelectedModificationButton.get_db_repr(smb), res["smb"]))
        res["pi"] = res["pi"].image_id

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in OrderItem.LONG_TO_SHORT.items()}
        args.setdefault("selected_modification_button_data", [])
        args["selected_modification_button_data"] = \
            list(map(lambda mod_button: SelectedModificationButton.document_repr_to_object(mod_button), args["selected_modification_button_data"]))
        args["preview_image"] = Image(doc[args["preview_image"]])

        return OrderItem(**args)

    def shorten_field_name(self, field_name):
        return OrderItem.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return OrderItem.SHORT_TO_LONG.get(field_name, None)
