import json

from bson import ObjectId
from web_framework_v2 import HttpRequest, JwtSecurity, QueryParameter, HttpResponse, HttpStatus, RequestBody

from api import auth_fail
from database import User, refresh_token_blacklist, access_token_blacklist
from security import RegistrationTokenFactory, LoginTokenFactory, AuthenticationResult, BlacklistJwtTokenAuth
from . import app


def register_fail(req: HttpRequest, res: HttpResponse, data: AuthenticationResult):
    res.status = HttpStatus.UNAUTHORIZED
    return json.dumps({
        "token": None,
        "auth_status": data.value,
        "auth_status_text": data.name,
    })


@RegistrationTokenFactory(on_fail=register_fail)
@app.post("/auth/register")
def register(
        factory_result: RegistrationTokenFactory,
):
    token: str = factory_result

    return {
        "access_token": token,
        "refresh_token": refresh_token_from_access_token(token),
        "auth_status": AuthenticationResult.Success.value
    }


@LoginTokenFactory(on_fail=auth_fail)
@app.post("/auth/login")
def login(
        token_created: LoginTokenFactory,
):
    token_created: str = token_created

    return {
        "access_token": token_created,
        "refresh_token": refresh_token_from_access_token(token_created)
    }


@BlacklistJwtTokenAuth(on_fail=auth_fail)
@app.post("/auth/logout")
def logout(
        raw_user: BlacklistJwtTokenAuth,
        response: HttpResponse,
        data: RequestBody()
):
    raw_user: User = raw_user
    if 'access_token' not in data or 'refresh_token' not in data:
        response.status = HttpStatus.BAD_REQUEST
        return {
            'error': 'Must pass "refresh_token" and "access_token" in request body'
        }

    refresh_token = data['refresh_token']
    access_token = data['access_token']

    if JwtSecurity.decode_refresh_token(refresh_token):
        refresh_token_blacklist.add_to_blacklist(refresh_token)

    if JwtSecurity.decode_access_token(access_token):
        access_token_blacklist.add_to_blacklist(access_token)


@app.get("/auth/refresh")
def refresh_access_token(token: QueryParameter(query_name="token"), res: HttpResponse):
    if token is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must pass query parameter 'token'"}

    result = JwtSecurity.decode_refresh_token(token)

    if result is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    if refresh_token_blacklist.in_blacklist(token):
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    _id = ObjectId(result["id"])
    user = User.get_by_id(_id, raw_document=False)
    if user is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    return {
        'access_token': user.build_access_token(sign=True),
        'refresh_token': token,
    }


@app.get("/auth/refresh/refresh")
def refresh_refresh_token(token: QueryParameter(query_name="token"), res: HttpResponse):
    if token is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must pass query parameter 'token'"}

    result = JwtSecurity.decode_refresh_token(token)

    if result is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    if refresh_token_blacklist.in_blacklist(token):
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    _id = ObjectId(result["id"])
    user = User.get_by_id(_id, raw_document=False)
    if user is None:
        res.status = HttpStatus.UNAUTHORIZED
        return {"error": "Must be a valid refresh token"}

    access_token = user.build_access_token(sign=True)
    refresh_token_blacklist.add_to_blacklist(token)
    return {
        "refresh_token": refresh_token_from_access_token(access_token),
        "access_token": access_token
    }


@app.get("/jwt/public")
def get_public_keys():
    return {
        "access_key": JwtSecurity.access_key.public,
        "refresh_key": JwtSecurity.refresh_key.public,
    }


def refresh_token_from_access_token(token: str):
    access_token = JwtSecurity.decode_access_token(token)
    refresh_token_data = {
        "id": access_token["id"]
    }

    return JwtSecurity.create_refresh_token(refresh_token_data, expiration_seconds=refresh_token_blacklist.expiration_time)
