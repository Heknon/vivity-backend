import json

from web_framework_v2 import HttpRequest, JwtSecurity, QueryParameter, HttpResponse, HttpStatus

from api import auth_fail
from security import RegistrationTokenFactory, LoginTokenFactory, AuthenticationResult
from . import app


def register_fail(req: HttpRequest, res: HttpResponse, data: AuthenticationResult):
    res.status = HttpStatus.UNAUTHORIZED
    print(req.body)
    return json.dumps({
        "token": None,
        "auth_result": data.value,
        "auth_result_text": data.name,
    })


@RegistrationTokenFactory(on_fail=register_fail)
@app.post("/user/register")
def register(
        factory_result: RegistrationTokenFactory,
):
    return json.dumps({
        "token": factory_result,
        "auth_result": AuthenticationResult.Success.value
    })


@LoginTokenFactory(on_fail=auth_fail)
@app.post("/user/login")
def login(
        token_created: LoginTokenFactory,
):
    return {
        "token": token_created
    }


@app.get("/user/verify")
def verify_token(token: QueryParameter(query_name="token"), res: HttpResponse):
    if token is None:
        res.status = HttpStatus.UNAUTHORIZED
        return False

    result = JwtSecurity.decode_token(token)
    if result is None:
        res.status = HttpStatus.UNAUTHORIZED
        return False

    return True
