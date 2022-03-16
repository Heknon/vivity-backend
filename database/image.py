"""
TODO: Implement Image class that interacts with AWS S3 storage for images.
"""
from __future__ import annotations

from database import s3Bucket


class Image:
    def __init__(self, image_id: str):
        self.image_id = image_id

    def __repr__(self):
        return self.image_id

    def get_image(self) -> bytes:
        return s3Bucket.get(self.image_id)[0]

    def delete_image(self):
        return s3Bucket.delete(self.image_id)

    @staticmethod
    def upload(image: bytes) -> Image:
        res = s3Bucket.upload(image, "png")
        if "key" not in res:
            raise RuntimeError("Failed to upload image.\n" + res)

        return Image(res["key"])
