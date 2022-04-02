from typing import List

from database import Image


class ModificationButton:
    def __init__(self, name, preferred_side, data: List[object], data_type: int, multi_select: bool):
        self.name = name
        self.preferred_side = preferred_side
        self.data = data
        self.data_type = data_type
        self.multi_select = multi_select


class ItemCreation:
    def __init__(self, title: str, subtitle: str, price: float, brand: str, category: str, tags: List[str]):
        self.title = title
        self.subtitle = subtitle
        self.price = price
        self.brand = brand
        self.category = category
        self.tags = tags


class ItemUpdate:
    def __init__(
            self,
            title: str,
            subtitle: str,
            description: str,
            price: float,
            brand: str,
            category: str,
            add_tags: List[str],
            remove_tags: List[str],
            tags: List[str],
            stock: int,
            modification_buttons: List[ModificationButton],
    ):
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.price = price
        self.brand = brand
        self.category = category
        self.add_tags = add_tags
        self.remove_tags = remove_tags
        self.stock = stock
        self.modification_buttons = modification_buttons
        self.tags = tags


class Review:
    def __init__(self, poster_id: bytes, pfp_id: str, poster_name: str, rating: float, text_content: str, image_ids: List[str]):
        self.poster_id = poster_id
        self.pfp_id = pfp_id
        self.poster_name = poster_name
        self.rating = rating
        self.text_content = text_content
        self.image_ids = image_ids
