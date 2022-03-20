from __future__ import annotations

import logging

from bson import ObjectId
from web_framework_v2 import JwtTokenFactory, JwtTokenAuth

from database import User, BusinessUser, blacklist
from security import AuthenticationResult, EMAIL_REGEX, VALIDATOR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_email(email: str):
    return EMAIL_REGEX.match(email)


class RegistrationTokenFactory(JwtTokenFactory):
    def __init__(self, on_fail=lambda request, response: None):
        super().__init__(on_fail, blacklist.TOKEN_EXPIRATION_TIME)

    def token_data_builder(self, request, request_body, user: User):
        return user.build_token()

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
        return user.build_token()

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
        if "bid" in user_doc and user_doc["bid"] is not None:
            user = BusinessUser.document_repr_to_object(user_doc)
        else:
            user = User.document_repr_to_object(user_doc)

        return True, AuthenticationResult.Success, user


class BlacklistJwtTokenAuth(JwtTokenAuth):
    def __init__(self, on_fail=lambda request, response: None, check_blacklist: bool = False, raw_document=False, no_fail=False, fail_on_null_result=True):
        super().__init__(on_fail, fail_on_null_result)
        self.check_blacklist = check_blacklist
        self.raw_document = raw_document
        self.no_fail = no_fail

    def authenticate(self, request, request_body, token) -> (bool, object):
        if self.no_fail:
            return True, AuthenticationResult.Success

        logger.debug(f"Trying token {token}")
        if token is None:
            return False, AuthenticationResult.TokenInvalid
        elif self.check_blacklist and self.is_token_blacklisted(request.headers["authorization"][8:]):
            return False, AuthenticationResult.PresentInBlacklist

        return True, AuthenticationResult.Success

    @staticmethod
    def is_token_blacklisted(token: str):
        return blacklist.in_blacklist(token)

    @staticmethod
    def blacklist_token(token):
        blacklist.add_to_blacklist(token)

    def decoded_token_transformer(self, request, request_body, decoded_token: dict) -> User | BusinessUser:
        if decoded_token is None:
            return None

        return User.get_by_id(ObjectId(decoded_token["id"]), self.raw_document)


class BusinessJwtTokenAuth(BlacklistJwtTokenAuth):
    """
    Authenticate only if user is a business owner.
    """

    def authenticate(self, request, request_body, token) -> (bool, object):
        base_auth_result = super().authenticate(request, request_body, token)
        if not base_auth_result[0]:
            return base_auth_result

        if "business_id" in token and token["business_id"] is not None:
            return True, AuthenticationResult.Success

        return False, AuthenticationResult.NotBusiness
