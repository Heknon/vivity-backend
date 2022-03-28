from collections import Iterable
from pathlib import Path
from typing import Union

from bson import ObjectId
from web_framework_v2 import RequestBody, QueryParameter, ContentType, HttpResponse, HttpStatus

from api import auth_fail
from body import UserSettings, PaymentData, DictNoNone
from database import User, BusinessUser, Image
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
            get_cart: QueryParameter("liked_items", bool),
    ):
        user: Union[User, BusinessUser] = user
        print(user.profile_picture)
        result = {
            "_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "options": user.options,
            "addresses": user.shipping_addresses,
            "liked_items": user.liked_items,
            "profile_picture": None if len(str(user.profile_picture)) == 0 else str(user.profile_picture),
            "cart": user.cart,
        }

        if type(user) is BusinessUser:
            result["business_id"] = str(user.business_id)

        if user.is_system_admin:
            result["is_system_admin"] = True

        if get_options is None and order_ids is None and get_address is None and get_liked_items is None:
            result["order_history"] = user.get_order_history()
            return result

        if not get_options:
            del result["options"]

        if not get_address:
            del result["addresses"]

        if not get_liked_items:
            del result["liked_items"]

        if not get_cart:
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

        if len(update) == 0:
            return f"Must pass at least one of the following fields: {user.options.updatable_fields}"

        return user.options.update_fields(**update).options

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/profile_picture", content_type=ContentType.text)
    def update_profile_picture(
            user: BlacklistJwtTokenAuth,
            pfp_data: RequestBody(raw_format=True)
    ):
        user: User = user
        pfp = None if pfp_data is None or len(pfp_data) == 0 else pfp_data
        if user.profile_picture is not None and user.profile_picture.image_id is not None:
            user.profile_picture.delete_image("profiles/")

        image = Image.upload(pfp, folder_name="profiles/") if pfp is not None else None
        user = user.update_profile_picture(image)

        return {
            "image_id": user.profile_picture
        }

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/profile_picture", content_type=ContentType.jpg)
    def get_profile_picture(
            user: BlacklistJwtTokenAuth
    ):
        user: User = user
        result = user.profile_picture.get_image("profiles/") if user.profile_picture.image_id is not None else None
        return result

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/favorite")
    def add_to_favorites(
            user: BlacklistJwtTokenAuth,
            res: HttpResponse,
            item_id: QueryParameter("item_id", str)
    ):
        user: User = user
        if not isUserId(item_id):
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": "query parameter item_id must be a valid string id"
            }

        return user.liked_items.add_liked_items(ObjectId(item_id)).liked_items

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.delete("/user/favorite")
    def remove_from_favorites(
            user: BlacklistJwtTokenAuth,
            res: HttpResponse,
            item_id: QueryParameter("item_id", str)
    ):
        user: User = user
        if not isUserId(item_id):
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": "query parameter item_id must be a valid string id"
            }

        return user.liked_items.remove_liked_item(ObjectId(item_id)).liked_items

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/user/payment")
    def user_payment(
            token_data: BlacklistJwtTokenAuth,
            payment_data: RequestBody(PaymentData)
    ):
        pass


def isUserId(s: str) -> bool:
    if not isinstance(s, str):
        return False

    try:
        ObjectId(s)
        return True
    except:
        return False
