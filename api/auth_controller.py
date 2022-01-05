from api import auth_fail
from body import UserInfo
from web_framework_v2 import RequestBody, HttpResponse
from . import app
from security import RegistrationTokenFactory, LoginTokenFactory


# TODO: Update authentication failures to be much more abstract
@RegistrationTokenFactory(on_fail=auth_fail)
@app.post("/user/register")
def register(
        factory_result: RegistrationTokenFactory,
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    return factory_result


@LoginTokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(
        token_created: LoginTokenFactory,
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    return token_created
