from __future__ import annotations

import logging
import re

from bson import ObjectId
from password_validator import PasswordValidator
from web_framework_v2 import JwtTokenFactory, JwtTokenAuth

from database import User, BusinessUser, blacklist
from security import AuthenticationResult

logger = logging.getLogger(__name__)

VALIDATOR = PasswordValidator().min(8).digits().lowercase().uppercase().symbols()
EMAIL_REGEX = re.compile(
    r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$')


def validate_email(email: str):
    return EMAIL_REGEX.match(email)


class RegistrationTokenFactory(JwtTokenFactory):
    def __init__(self, on_fail=lambda request, response: None):
        super().__init__(on_fail, blacklist.TOKEN_EXPIRATION_TIME)

    def token_data_builder(self, request, request_body, user: User):
        return {
            "id": user._id.binary.decode("cp437"),
            "name": user.name,
            "profile_picture": user.profile_picture.image_id,
            "email": user.email,
            "phone": user.phone
        }

    def authenticate(self, request, request_body) -> (bool, object, User):
        if "name" not in request_body or "email" not in request_body or "password" not in request_body or "phone" not in request_body:
            return False, AuthenticationResult.MissingFields, None

        email = request_body["email"]
        password = request_body["password"]

        if not VALIDATOR.validate(password):
            return False, AuthenticationResult.PasswordInvalid, None
        elif not validate_email(email):
            return False, AuthenticationResult.EmailInvalid, None
        elif User.exists_by_email(email):
            return False, AuthenticationResult.EmailExists, None

        user = User.create_new_user(
            email,
            request_body["name"],
            request_body["phone"],
            password,
            True
        )

        return True, AuthenticationResult.Success, user


class LoginTokenFactory(JwtTokenFactory):
    def __init__(self, on_fail=lambda request, response: None):
        super().__init__(on_fail, blacklist.TOKEN_EXPIRATION_TIME)

    def token_data_builder(self, request, request_body, user: User | BusinessUser):
        result = {
            "id": user._id.binary.decode("cp437"),
            "name": user.name,
            "profile_picture": user.profile_picture.image_id,
            "email": user.email,
            "phone": user.phone
        }

        if hasattr(user, "business_id"):
            result["business_id"] = user.business_id

        return result

    def authenticate(self, request, request_body) -> (bool, object, object):
        if "email" not in request_body or "password" not in request_body:
            return False, AuthenticationResult.MissingFields, None

        email = request_body["email"]
        password = request_body["password"]

        if not VALIDATOR.validate(password):
            return False, AuthenticationResult.PasswordInvalid, None
        elif not validate_email(email):
            return False, AuthenticationResult.EmailInvalid, None

        user_doc: dict | None = User.get_by_email(email)

        if user_doc is None:
            return False, AuthenticationResult.EmailIncorrect, None

        if not User.compare_to_hash(password, user_doc["pw"]):
            return False, AuthenticationResult.PasswordIncorrect, None

        user: User | BusinessUser
        if "business_id" in user_doc and user_doc["business_id"] is not None:
            user = BusinessUser.document_repr_to_object(user_doc)
        else:
            user = User.document_repr_to_object(user_doc)

        return True, AuthenticationResult.Success, user


class BlacklistJwtTokenAuth(JwtTokenAuth):
    def __init__(self, on_fail=lambda request, response: None, check_blacklist: bool = False):
        super().__init__(on_fail)
        self.check_blacklist = check_blacklist

    def authenticate(self, request, request_body, token) -> (bool, object):
        if token is None:
            return False, AuthenticationResult.TokenInvalid
        elif self.check_blacklist and self.is_token_blacklisted(request.headers["Authorization"][8:]):
            return False, AuthenticationResult.PresentInBlacklist

        return True, AuthenticationResult.Success

    @staticmethod
    def is_token_blacklisted(token: str):
        return blacklist.in_blacklist(token)

    @staticmethod
    def blacklist_token(token):
        blacklist.add_to_blacklist(token)

    def decoded_token_transformer(self, request, request_body, decoded_token: dict) -> User | BusinessUser:
        if "business_id" in decoded_token and decoded_token["business_id"] is not None:
            return BusinessUser.get_by_id(ObjectId(decoded_token["id"].encode("cp437")))
        return User.get_by_id(ObjectId(decoded_token["id"].encode("cp437")))


class BusinessJwtTokenAuth(BlacklistJwtTokenAuth):
    """
    Authenticate only if user is a business owner.
    """

    def authenticate(self, request, request_body, token) -> (bool, object):
        base_auth_result = super().authenticate(request, request_body, token)
        if not base_auth_result[0]:
            return base_auth_result

        if "business_name" in token and token["business_name"] is not None:
            return True, AuthenticationResult.Success

        return False, AuthenticationResult.NotBusiness
