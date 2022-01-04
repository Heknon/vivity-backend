from typing import List


class ModificationButton:
    def __init__(self, name, preferred_side, data: List[bytes], data_type: int, multi_select: bool):
        self.name = name
        self.preferred_side = preferred_side
        self.data = data
        self.data_type = data_type
        self.multi_select = multi_select


class ItemCreation:
    def __init__(self, title: str, price: float, brand: str, category: str, tags: List[str]):
        self.title = title
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
            add_image: bytes,
            remove_image: int,
            remove_modification_button: int,
            add_modification_button: ModificationButton,
            stock: int
    ):
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.price = price
        self.brand = brand
        self.category = category
        self.add_tags = add_tags
        self.remove_tags = remove_tags
        self.add_image = add_image
        self.remove_image = remove_image
        self.remove_modification_button = remove_modification_button
        self.add_modification_button = add_modification_button
        self.stock = stock


class Review:
    def __init__(self, poster_id: bytes, pfp_id: bytes, poster_name: str, rating: float, text_content: str, image_ids: List[str]):
        self.poster_id = poster_id
        self.pfp_id = pfp_id
        self.poster_name = poster_name
        self.rating = rating
        self.text_content = text_content
        self.image_ids = image_ids
