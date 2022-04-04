__all__ = ["auth_fail", "app", "HOST"]

import logging

logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO
                    )

from web_framework_v2 import Framework, JwtSecurity, HttpStatus, HttpResponse, HttpRequest

JwtSecurity.set_secret("some_super_secret")


def error_handler(error: Exception, traceback: str, req: HttpRequest, res: HttpResponse, path_variables: dict):
    logging.exception(error)
    res.statusCode = HttpStatus.BAD_REQUEST
    return {
        "error": str(error)
    }


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
