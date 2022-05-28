__all__ = ["auth_fail", "app", "HOST"]

import json
import logging
import os

logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
                    )

from web_framework_v2 import Framework, JwtSecurity, HttpStatus, HttpResponse, HttpRequest, KeyPair

JwtSecurity.set_access_key(
    KeyPair(
        os.getenv("JWT_ACCESS_PUBLIC_KEY").replace("\\n", '\n'),
        os.getenv("JWT_ACCESS_PRIVATE_KEY").replace("\\n", '\n')
    )
)

JwtSecurity.set_refresh_key(
    KeyPair(
        os.getenv("JWT_REFRESH_PUBLIC_KEY").replace("\\n", '\n'),
        os.getenv("JWT_REFRESH_PRIVATE_KEY").replace("\\n", '\n')
    )
)

REVIEW_IMAGE_AWS_FOLDER = "reviews/"
ITEM_IMAGE_AWS_FOLDER = "items/"
PROFILE_PICTURE_AWS_FOLDER = "profiles/"
BUSINESS_OWNER_ID_AWS_FOLDER = "business_ids/"


def error_handler(error: Exception, traceback: str, req: HttpRequest, res: HttpResponse, path_variables: dict):
    logging.exception(error)
    res.status = HttpStatus.BAD_REQUEST
    res.content_type = "application/json"
    return json.dumps({
        "error": str(error)
    })


HOST = "0.0.0.0"
app = Framework(
    static_folder="",
    static_url_path="",
    host=HOST,
    port=80,
    log_level=logging.INFO,
    error_handler=error_handler
)

from .api_utils import auth_fail
from . import user
from . import business
from . import auth_controller
from . import search_controller
from . import assets_controller
from . import admin_controller
