from __future__ import annotations

from typing import List

import jsonpickle

from database import DocumentObject
from database.business.item import ModificationButtonDataType


class SelectedModificationButton(DocumentObject):
    LONG_TO_SHORT = {
        "name": "nm",
        "selected_data": "sd",
        "data_type": "dt"
    }

    SHORT_TO_LONG = {value: key for key, value in LONG_TO_SHORT.items()}

    def __init__(self, name: str, selected_data: List[str], data_type: ModificationButtonDataType):
        self.name = name
        self.selected_data = selected_data
        self.data_type = data_type

    def __repr__(self):
        return jsonpickle.encode(SelectedModificationButton.get_db_repr(self, True), unpicklable=False)

    @staticmethod
    def get_db_repr(
            selected_modification_button: SelectedModificationButton,
            get_long_names: bool = False
    ) -> dict:
        res = {value: getattr(selected_modification_button, key) for key, value in SelectedModificationButton.LONG_TO_SHORT.items()}
        res["dt"] = selected_modification_button.data_type.value

        if get_long_names:
            res["sd"] = list(map(lambda data: data if isinstance(data, str) else int(data), res["sd"]))
            res = {selected_modification_button.lengthen_field_name(key): value for key, value in res.items()}

        return res

    @staticmethod
    def document_repr_to_object(doc, **kwargs):
        args = {key: doc[value] for key, value in SelectedModificationButton.LONG_TO_SHORT.items()}
        args["data_type"] = ModificationButtonDataType._value2member_map_[args["data_type"]]

        return SelectedModificationButton(**args)

    def shorten_field_name(self, field_name):
        return self.LONG_TO_SHORT.get(field_name, None)

    def lengthen_field_name(self, field_name):
        return self.SHORT_TO_LONG.get(field_name, None)
