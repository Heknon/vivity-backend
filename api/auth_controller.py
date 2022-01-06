import json

from api import auth_fail
from body import UserInfo
from web_framework_v2 import RequestBody, HttpResponse
from . import app
from security import RegistrationTokenFactory, LoginTokenFactory


@RegistrationTokenFactory(on_fail=auth_fail)
@app.post("/user/register")
def register(
        factory_result: RegistrationTokenFactory,
):
    return factory_result


@LoginTokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(
        token_created: LoginTokenFactory,
):
    return token_created
