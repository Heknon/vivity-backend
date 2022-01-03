from web_framework_v2 import RequestBody, HttpResponse, JwtTokenAuth, QueryParameter

from api.user import auth_fail
from main import app
from models import UserSettings, ForgotPasswordAuthorizedRouteRequestBody, AuthorizedRouteRequestBody


# TODO: Remember to add blacklist checks of token

class UserData:
    """
    handles user data
    """

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.get("/user")
    def get_user_data(
            get_options: QueryParameter("options", bool),
            get_orders: QueryParameter("orders", bool),
            order_ids: QueryParameter("order", list),
            get_address: QueryParameter("address", bool),
            get_liked_items: QueryParameter("liked_items", bool),
    ):
        # TODO: Check if crash occurs when get_orders gets list
        # TODO: Check if crash occurs when order_ids gets int
        pass

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user")
    def update_user_data(user_settings: RequestBody(UserSettings)):
        pass
