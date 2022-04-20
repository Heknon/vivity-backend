import logging
from typing import Union

from bson import ObjectId
from web_framework_v2 import RequestBody, QueryParameter, JwtSecurity, HttpResponse, HttpStatus, HttpRequest

from api import auth_fail, HOST
from communication import email_service
from database import User, BusinessUser, access_token_blacklist
from database.user_auth import UserAuth
from security import BlacklistJwtTokenAuth, EMAIL_REGEX, VALIDATOR
from .. import app

logger = logging.getLogger(__name__)


class UserAuthController:
    @staticmethod
    @app.post("/user/forgot")
    def send_forgot_password_email(
            data: RequestBody(),
            response: HttpResponse
    ):
        email = data['email'] if 'email' in data else None
        # TODO: Switch to deep linking.
        if email is None or not EMAIL_REGEX.match(email):
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "Invalid email address! Must pass a valid email as a query parameter.\nExample: '?email=host@domain.com'"
            }

        user_exists: bool = User.exists_by_email(email)
        if not user_exists:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "A user with this email does not exist."
            }

        # TODO: Move to different key pair
        token = JwtSecurity.create_access_token({
            "email": email
        }, access_token_blacklist.TOKEN_EXPIRATION_TIME)
        url = f"http://{HOST}/user/password/forgot?temporary_auth={token}"

        email_service.send_forgot_password(
            email,
            url
        )

        return {
            "success": True
        }

    @staticmethod
    @BlacklistJwtTokenAuth(no_fail=True, fail_on_null_result=False)
    @app.patch("/user/password/forgot")
    def update_user_password(
            request: HttpRequest,
            response: HttpResponse,
            data: RequestBody(),
            user: BlacklistJwtTokenAuth = None
    ):
        if 'temporary_auth' not in data:
            response.status = HttpStatus.BAD_REQUEST
            return {
                'error': 'Must pass "temporary_auth" token field in json payload'
            }

        temporary_auth_token = data['temporary_auth']
        parsed_token = JwtSecurity.decode_access_token(temporary_auth_token)

        if parsed_token is None:
            response.status = HttpStatus.UNAUTHORIZED
            return {
                'error': 'Invalid authentication token.'
            }

        if "password" not in data:
            response.status = HttpStatus.BAD_REQUEST
            return {
                'error': 'Must pass "password" field in json payload'
            }
        elif not VALIDATOR.validate(data["password"]):
            response.status = HttpStatus.BAD_REQUEST
            return {
                'error': f"Must pass a valid password. {VALIDATOR.properties}"
            }

        new_password = data['password']

        if access_token_blacklist.in_blacklist(temporary_auth_token):
            return "You have already reset your password using this temporary_auth token"

        user = User.get_by_email(parsed_token["email"], False)
        if user is None:
            response.status = HttpStatus.UNAUTHORIZED
            return f"No user found with email {parsed_token['email']}"

        user = user.update_password(new_password)
        access_token_blacklist.add_to_blacklist(temporary_auth_token)

        return {
            "access_token": user.build_access_token(True).encode()
        }

    @staticmethod
    @BlacklistJwtTokenAuth()
    @app.post("/user/password")
    def reset_password(
            raw_user: BlacklistJwtTokenAuth,
            payload: RequestBody(),
            response: HttpResponse,
    ):
        if 'new_password' not in payload or 'password' not in payload:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "Must provide 'password' and 'new_password'"
            }

        current_password = payload['password']
        new_password = payload['new_password']
        if not VALIDATOR.validate(new_password):
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"Must pass a valid password. {VALIDATOR.properties}"
            }

        user: User = raw_user
        if not user.compare_hash(current_password):
            response.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Wrong password"
            }

        if current_password == new_password:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "New password must be different"
            }

        user = user.update_password(new_password)
        return {
            "access_token": user.build_access_token(sign=True)
        }

    @staticmethod
    @app.get("/auth/otp")
    def is_otp_enabled(
            email: QueryParameter(query_name="email"),
            _id: QueryParameter(query_name="id"),
            response: HttpResponse
    ):
        if email is None and _id is None:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"Must pass query parameter 'email' or 'id'"
            }
        using_id = _id is not None
        _id = ObjectId(_id) if using_id else None
        user_auth = UserAuth.get_by_id(_id) if using_id else UserAuth.get_by_email(email)
        if user_auth is None:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"No user with email {email} or id {_id}"
            }

        return {
            "enabled": user_auth.has_2fa
        }

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/auth/otp")
    def enable_otp(
            raw_user: BlacklistJwtTokenAuth,
            response: HttpResponse
    ):
        user: User = raw_user
        user_auth = UserAuth.turn_on_otp(user.id)
        response.status = HttpStatus.ACCEPTED
        return {
            "secret": user_auth.otp_secret
        }

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/auth/otp")
    def disable_otp(
            raw_user: BlacklistJwtTokenAuth,
            response: HttpResponse
    ):
        user: User = raw_user
        UserAuth.turn_off_otp(user.id)
        response.status = HttpStatus.NO_CONTENT


class DeleteUser:
    """
    handle user deletion routes
    """

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/delete")
    def delete_user(
            user: BlacklistJwtTokenAuth,
            response: HttpResponse
    ):
        # TODO: Deletion confirmation system with tokens like forgot password
        user: Union[User, BusinessUser] = user
        User.delete_by_id(user._id)
        response.status = HttpStatus.NO_CONTENT
        return "Successfully deleted!"
