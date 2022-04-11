import base64
import logging
import os

from web_framework_v2 import QueryParameter, RequestBody, HttpResponse, HttpStatus

from api import app, auth_fail, ITEM_IMAGE_AWS_FOLDER, REVIEW_IMAGE_AWS_FOLDER, PROFILE_PICTURE_AWS_FOLDER
from database import Image, s3Bucket, User
from security import BlacklistJwtTokenAuth


def image_error_handler(err, traceback, req, res, path_vars) -> object:
    return {"error": "Image not found", 'error_type': str(type(err))} if "Unable to access bucket" in str(err) else None


aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
bucket_name = os.getenv("AWS_BUCKET_NAME")


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
    @app.post("/image/multi", error_handler=image_error_handler)
    def get_image(
            raw_user: BlacklistJwtTokenAuth,
            images: RequestBody(),
            response: HttpResponse,
    ):
        user: User = raw_user
        allowed_routes = {ITEM_IMAGE_AWS_FOLDER, PROFILE_PICTURE_AWS_FOLDER, REVIEW_IMAGE_AWS_FOLDER}

        if not isinstance(images, list):
            response.status = HttpStatus.BAD_REQUEST
            return {
                'error': "Must must payload of type list"
            }

        if images is None or len(images) == 0:
            response.status = HttpStatus.BAD_REQUEST
            return {}

        unique_image_list = list(set(images))
        images = []
        for image in unique_image_list:
            split = image.split("/")
            contains = False
            for split_item in split:
                if split_item + '/' in allowed_routes:
                    contains = True
                    break

            if contains or user.is_system_admin:
                images.append(image)

        result = {}

        try:
            for key, data in s3Bucket.fetch_all(*images):
                result[key] = base64.b64encode(data).decode('utf-8')

            return result
        except Exception as e:
            logging.exception(e)
            return {
                'error': e
            }
