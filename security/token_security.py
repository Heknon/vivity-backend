from web_framework_v2 import JwtTokenFactory, JwtTokenAuth

from security import AuthenticationResult


class RegistrationTokenFactory(JwtTokenFactory):
    def token_data_builder(self, request, request_body, data):
        return {
            "id": data[0],
            "name": request_body["name"],
            "pfp_id": data[1],
            "email": request_body["email"],
            "phone": request_body["phone"]
        }

    def authenticate(self, request, request_body) -> (bool, object, object):
        if "name" not in request_body or "email" not in request_body or "password" not in request_body or "phone" not in request_body:
            return False, AuthenticationResult.MissingFields, None

        # Check that email isnt in db
        # validate password
        user_id: bytes
        pfp_id: str
        return True, AuthenticationResult.Success, (user_id, pfp_id)


class LoginTokenFactory(JwtTokenFactory):
    def token_data_builder(self, request, request_body, user_document):
        result = {
            "id": user_document.id,
            "name": user_document.name,
            "pfp_id": user_document.pfp_id,
            "email": user_document.email,
            "phone": user_document.phone
        }

        if "business_name" in user_document and user_document["business_name"] is not None:
            result["business_name"] = user_document.business_name
            result["business_id"] = user_document.business_id

        return result

    def authenticate(self, request, request_body) -> (bool, object, object):
        if "email" not in request_body or "password" not in request_body:
            return False, AuthenticationResult.MissingFields, None

        email = request_body["email"]
        password = request_body["password"]
        hashed_db_password: str  # get hashed password and compare them.
        user_document: object

        return True, AuthenticationResult.Success, user_document


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
        # Todo: Check if token is blacklisted in database
        pass

    @staticmethod
    def blacklist_token(token):
        # Todo: Add token to blacklist
        pass


class BusinessJwtTokenAuth(BlacklistJwtTokenAuth):
    """
    Authenticate only if user is a business owner.
    """

    def authenticate(self, request, request_body, token) -> (bool, object):
        base_auth_result = super().authenticate(request, request_body, token)
        if not base_auth_result:
            return False

        if "business_name" in token and token["business_name"] is not None:
            return True, AuthenticationResult.Success

        return False, AuthenticationResult.NotBusiness
