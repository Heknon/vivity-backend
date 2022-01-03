from body import UserInfo
from web_framework_v2 import RequestBody, HttpResponse
from main import app
from security import TokenFactory


def auth_fail(req, res):
    pass


@TokenFactory
@app.post("/user/register")
def register(user_info: RequestBody(UserInfo), response: HttpResponse):
    pass


@TokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(user_info: RequestBody(UserInfo), response: HttpResponse):
    pass
