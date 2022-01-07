__all__ = ["auth_fail", "app"]

import logging

logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

from web_framework_v2 import Framework, JwtSecurity

app = Framework("", "", logging.INFO)
JwtSecurity.set_secret("some_super_secret")

from .api_utils import auth_fail
from . import user
from . import business
from . import auth_controller
from . import feed_controller

