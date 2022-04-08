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
    port=20200,
    log_level=logging.INFO,
    error_handler=error_handler
)

from .api_utils import auth_fail
from . import user
from . import business
from . import auth_controller
from . import feed_controller
from . import assets_controller
from . import admin_controller
