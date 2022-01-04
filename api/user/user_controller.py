from web_framework_v2 import RequestBody, JwtTokenAuth, QueryParameter

from api import auth_fail
from body import UserSettings, PaymentData
from .. import app


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

    @staticmethod
    @JwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/payment")
    def user_payment(
            token_data: JwtTokenAuth,
            payment_data: RequestBody(PaymentData)
    ):
        pass
