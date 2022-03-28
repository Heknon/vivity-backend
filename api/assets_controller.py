from web_framework_v2 import QueryParameter

from api import app, auth_fail
from database import Image
from security import BlacklistJwtTokenAuth


class AssetsController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/image")
    def get_image(
            user: BlacklistJwtTokenAuth,
            image_id: QueryParameter("image_id"),
            folder_name: QueryParameter("folder_name")
    ):
        try:
            return Image(folder_name + image_id).get_image()
        except:
            return {
                "error": "Image not found."
            }
