__all__ = ["auth_fail", "app"]

from web_framework_v2 import Framework, JwtSecurity

app = Framework("", "")
JwtSecurity.set_secret("some_super_secret")

from .api_utils import auth_fail
from . import user
from . import business
from . import auth_controller
from . import feed_controller
