from web_framework_v2 import JwtTokenAuth, RequestBody, QueryParameter

from api.user import auth_fail
from main import app
from models import ForgotPasswordAuthorizedRouteRequestBody, AuthorizedRouteRequestBody


class UserForgot:
    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/forgot")
    def send_forgot_password_email(email: QueryParameter("email")):
        pass

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user/forgot")
    def update_user_password(authorized_body: RequestBody(ForgotPasswordAuthorizedRouteRequestBody)):
        pass


class DeleteUser:
    """
    handle user deletion routes
    """

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/delete")
    def send_delete_email(email: QueryParameter("email")):
        pass

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/delete")
    def delete_user(authorized_body: RequestBody(AuthorizedRouteRequestBody)):
        pass