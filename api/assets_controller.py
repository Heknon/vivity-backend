import base64

from s3_bucket.exceptions import BucketAccessDenied
from web_framework_v2 import QueryParameter

from api import app, auth_fail
from database import Image
from security import BlacklistJwtTokenAuth


def image_error_handler(err, traceback, req, res, path_vars) -> object:
    return {"error": "Image not found", 'error_type': str(type(err))} if "Unable to access bucket" in str(err) else None


class AssetsController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/image", error_handler=image_error_handler)
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

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/image/multi", error_handler=image_error_handler)
    def get_image(
            user: BlacklistJwtTokenAuth,
            image_ids: QueryParameter("image_ids"),
            folder_name: QueryParameter("folder_name") = ""
    ):
        if not isinstance(image_ids, list):
            image_ids = [image_ids]

        image_ids = set(image_ids)
        images = dict()
        for image_id in image_ids:
            try:
                images[image_id] = base64.b64encode(Image(folder_name + image_id).get_image()).decode('utf-8')
            except BucketAccessDenied:
                continue

        return images
