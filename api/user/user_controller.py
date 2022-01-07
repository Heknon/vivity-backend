from collections import Iterable
from typing import Union

from web_framework_v2 import RequestBody, QueryParameter

from api import auth_fail
from body import UserSettings, PaymentData, DictNoNone
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
            order_ids: QueryParameter("orders", list),
            get_address: QueryParameter("addresses", bool),
            get_liked_items: QueryParameter("liked_items", bool),
    ):
        user: Union[User, BusinessUser] = user
        result = {
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "options": user.options,
            "addresses": user.shipping_addresses,
            "liked_items": user.liked_items
        }

        if type(user) is BusinessUser:
            result["business_id"] = str(user.business_id)

        if get_options is None and order_ids is None and get_address is None and get_liked_items is None:
            result["order_history"] = user.get_order_history()
            return result

        if not get_options:
            del result["options"]

        if not get_address:
            del result["addresses"]

        if not get_liked_items:
            del result["liked_items"]

        if order_ids == "all":
            result["order_history"] = user.get_order_history()
        elif order_ids is not None:
            order_history = user.get_order_history()
            ids = [order_ids] if not isinstance(order_ids, Iterable) else order_ids
            result["orders"] = []
            orders_length = len(order_history.orders) if order_history is not None else 0

            for index in ids:
                if int(index) >= orders_length or index < 0:
                    continue

                result["orders"].append(order_history.orders[index])

        return result

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user")
    def update_user_data(
            user: BlacklistJwtTokenAuth,
            user_settings: RequestBody(UserSettings)
    ):
        user: Union[User, BusinessUser] = user
        user_settings: UserSettings = user_settings

        update = DictNoNone(
            sweats_size=user_settings.sweats_size if hasattr(user_settings, "sweats_size") else None,
            jeans_size=user_settings.jeans_size if hasattr(user_settings, "jeans_size") else None,
            shirt_size=user_settings.shirt_size if hasattr(user_settings, "shirt_size") else None,
            currency_type=user_settings.currency_type if hasattr(user_settings, "currency_type") else None,
            distance_unit=user_settings.distance_unit if hasattr(user_settings, "distance_unit") else None,
            business_search_radius=user_settings.business_search_radius if hasattr(user_settings, "business_search_radius") else None
        )

        return user.options.update_fields(**update).options

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/payment")
    def user_payment(
            token_data: BlacklistJwtTokenAuth,
            payment_data: RequestBody(PaymentData)
    ):
        pass
