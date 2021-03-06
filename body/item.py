from typing import List


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
        self.stock = stock
        self.modification_buttons = modification_buttons
        self.tags = tags


class Review:
    def __init__(self, rating: float, text_content: str, images: List[str]):
        self.rating = rating
        self.text_content = text_content
        self.images = images
