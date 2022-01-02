from body import UserInfo
from framework import RequestBody, HttpResponse
from main import app
from security import TokenFactory


@TokenFactory
@app.post("/user/register")
def register(user_info: RequestBody(UserInfo), response: HttpResponse):
