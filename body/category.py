from typing import List


class UpdateCategoryData:
    def __init__(self, name: str, add_item_ids: List[str], remove_item_ids: List[str]):
        self.name = name
        self.add_item_ids = add_item_ids
        self.remove_item_ids = remove_item_ids
