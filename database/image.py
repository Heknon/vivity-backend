"""
TODO: Implement Image class that interacts with AWS S3 storage for images.
"""
from __future__ import annotations
import jsonpickle


class Image:
    def __init__(self, image_id: str):
        self.image_id = image_id

    def __repr__(self):
        return self.image_id

    def get_image(self) -> bytes:
        pass

    def delete_image(self):
        pass

    @staticmethod
    def upload(image: bytes) -> Image:
        # TODO: CREATE
        return Image("PLACEHOLDER-ID")
