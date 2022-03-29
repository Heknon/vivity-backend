"""
TODO: Implement Image class that interacts with AWS S3 storage for images.
"""
from __future__ import annotations

import uuid

from database import s3Bucket


class Image:
    def __init__(self, image_id: str):
        self.image_id = image_id

    def __repr__(self):
        return self.image_id

    def get_image(self, folder_name="") -> bytes:
        return s3Bucket.get(folder_name + self.image_id)

    def delete_image(self, folder_name=""):
        return s3Bucket.delete(folder_name + self.image_id)

    @staticmethod
    def upload(image: bytes, key=str(uuid.uuid4()), folder_name: str = "") -> Image:
        res = s3Bucket.upload(image, key, folder_name)
        if res is not None:
            raise RuntimeError("Failed to upload image.\n" + str(res))

        return Image(key)

    def __getstate__(self):
        return self.image_id

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self):
        return self.image_id if self.image_id is not None else ""
