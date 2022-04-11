from __future__ import annotations

import uuid

from database import s3Bucket


class Image:
    def __init__(self, image_id: str):
        self.image_id = image_id

    def __repr__(self):
        return self.image_id

    def get_image(self) -> bytes:
        return s3Bucket.get(self.image_id)

    def delete_image(self):
        return s3Bucket.delete(self.image_id)

    @staticmethod
    def upload(image: bytes, key=None, folder_name: str = "") -> Image:
        if key is None:
            key = str(uuid.uuid4())
        key = folder_name + key
        res = s3Bucket.upload(image, key)
        if res is not None:
            raise RuntimeError("Failed to upload image.\n" + str(res))

        return Image(key)

    def __getstate__(self):
        return self.image_id

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self):
        return self.image_id if self.image_id is not None else ""
