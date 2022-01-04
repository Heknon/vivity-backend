from api import auth_fail
from body import UserInfo
from web_framework_v2 import RequestBody, HttpResponse
from . import app
from security import RegistrationTokenFactory, LoginTokenFactory


@RegistrationTokenFactory
@app.post("/user/register")
def register(
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    pass


@LoginTokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(
        token_created: LoginTokenFactory,
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    pass
