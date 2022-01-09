from typing import Union

from web_framework_v2 import RequestBody, QueryParameter, JwtSecurity, HttpResponse, HttpStatus, HttpRequest

from api import auth_fail, HOST
from communication import email_service
from database import User, BusinessUser, blacklist
from security import BlacklistJwtTokenAuth, EMAIL_REGEX, VALIDATOR
from .. import app


class UserForgot:
    @staticmethod
    @app.post("/user/forgot")
    def send_forgot_password_email(
            email: QueryParameter("email"),
            response: HttpResponse
    ):
        # TODO: Switch to deep linking.
        if email is None or not EMAIL_REGEX.match(email):
            response.status = HttpStatus.BAD_REQUEST
            return "Invalid email address! Must pass a valid email as a query parameter.\nExample: '?email=host@domain.com'"

        user_exists: bool = User.exists_by_email(email)
        if not user_exists:
            response.status = HttpStatus.BAD_REQUEST
            return "A user with this email does not exist."

        token = JwtSecurity.create_token({
            "email": email
        }, blacklist.TOKEN_EXPIRATION_TIME)
        url = f"http://{HOST}/user/reset?temporary_auth={token}"

        email_service.send_forgot_password(
            email,
            url
        )

        return "Email sent."

    @staticmethod
    @BlacklistJwtTokenAuth(no_fail=True)
    @app.patch("/user/reset")
    def update_user_password(
            request: HttpRequest,
            response: HttpResponse,
            password: RequestBody(),
            temporary_auth: QueryParameter("temporary_auth"),
            user: BlacklistJwtTokenAuth = None
    ):
        if "password" not in password:
            return "Must pass 'password' field in request body."
        elif not VALIDATOR.validate(password["password"]):
            return f"Must pass a valid password. {VALIDATOR.properties}"

        user: Union[User, None] = user
        previous_token = request.headers.get("Authorization", None)
        used_temp_auth = False

        if temporary_auth is not None and user is None:
            if blacklist.in_blacklist(temporary_auth):
                return "You can only change your password once per reset request."
            res = JwtSecurity.decode_token(temporary_auth)

            if res is None:
                response.status = HttpStatus.UNAUTHORIZED
                return "Invalid reset token."

            user = User.get_by_email(res["email"], False)
            if user is None:
                response.status = HttpStatus.UNAUTHORIZED
                return f"No user found with email {res['email']}"

            used_temp_auth = True

        user = user.update_fields(password=user.hash_password(password["password"]))
        if previous_token is not None and len(previous_token) > 8:
            blacklist.add_to_blacklist(previous_token[8:])

        if used_temp_auth:
            blacklist.add_to_blacklist(temporary_auth)

        return user.build_token(True).encode()


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
