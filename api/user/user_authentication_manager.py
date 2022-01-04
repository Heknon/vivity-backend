from web_framework_v2 import RequestBody, QueryParameter

from api import auth_fail
from security import BlacklistJwtTokenAuth
from .. import app
from body import ForgotPasswordAuthorizedRouteRequestBody, AuthorizedRouteRequestBody


class UserForgot:
    @staticmethod
    @app.post("/user/forgot")
    def send_forgot_password_email(email: QueryParameter("email")):
        pass

    @staticmethod
    @app.patch("/user/forgot")
    def update_user_password(authorized_body: RequestBody(ForgotPasswordAuthorizedRouteRequestBody)):
        pass


class DeleteUser:
    """
    handle user deletion routes
    """

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/delete")
    def send_delete_email(
            token_data: BlacklistJwtTokenAuth
    ):
        pass

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/delete")
    def delete_user(
            token_data: BlacklistJwtTokenAuth,
            authorized_body: RequestBody(AuthorizedRouteRequestBody)
    ):
        pass
