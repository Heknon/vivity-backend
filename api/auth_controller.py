from api import auth_fail
from body import UserInfo
from web_framework_v2 import RequestBody, HttpResponse
from . import app
from security import TokenFactory


@app.post("/user/register")
def register(
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    pass


@TokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(
        token_created: TokenFactory,
        user_info: RequestBody(UserInfo),
        response: HttpResponse
):
    pass
