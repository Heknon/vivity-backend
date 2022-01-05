"""
TODO: Implement Image class that interacts with AWS S3 storage for images.
"""


class Image:
    def __init__(self, image_id: str):
        self.image_id = image_id

    def get_image(self) -> bytes:
        pass

    def delete_image(self):
        pass
