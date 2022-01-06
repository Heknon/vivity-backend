from typing import Union

from web_framework_v2 import RequestBody, QueryParameter

from api import auth_fail
from body import UserSettings, PaymentData
from database import User, BusinessUser
from security import BlacklistJwtTokenAuth
from .. import app


class UserData:
    """
    handles user data
    """

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user")
    def get_user_data(
            user: BlacklistJwtTokenAuth,
            get_options: QueryParameter("options", bool),
            get_orders: QueryParameter("orders", bool),
            order_ids: QueryParameter("order", list),
            get_address: QueryParameter("address", bool),
            get_liked_items: QueryParameter("liked_items", bool),
    ):
        user: Union[User, BusinessUser] = user

        result = {

        }

        return

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user")
    def update_user_data(user_settings: RequestBody(UserSettings)):
        pass

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/payment")
    def user_payment(
            token_data: BlacklistJwtTokenAuth,
            payment_data: RequestBody(PaymentData)
    ):
        pass
