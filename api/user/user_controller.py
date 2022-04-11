import base64
from typing import Union

from bson import ObjectId
from web_framework_v2 import RequestBody, QueryParameter, ContentType, HttpResponse, HttpStatus

from api import auth_fail
from body import UserSettings, PaymentData
from database import User, BusinessUser, Image, items_collection, Unit, Item, Business
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
            include_cart_item_models: QueryParameter("include_cart_item_models", bool),
            include_business: QueryParameter("include_business", bool),
    ):
        user: Union[User, BusinessUser] = user
        result = user.__getstate__()

        include_business = include_business if include_business is not None and isinstance(include_business, bool) else False
        if type(user) is BusinessUser and include_business:
            result['business'] = Business.get_business_by_id(user.business_id).__getstate__()

        if user.is_system_admin:
            result["is_system_admin"] = True

        include_cart_item_models = include_cart_item_models if include_cart_item_models is not None and isinstance(include_cart_item_models, bool) else False
        if include_cart_item_models:
            cart_item_ids = list(map(lambda x: x.item_id, user.cart.items))
            result["cart_item_models"] = list(map(lambda item: item.__getstate__(), Item.get_items(*cart_item_ids)))

        result['profile_picture'] = base64.b64encode(user.profile_picture.get_image('profiles/'))

        return result

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.patch("/user")
    def update_user_data(
            user: BlacklistJwtTokenAuth,
            user_settings: RequestBody(UserSettings),
            response: HttpResponse,
            include_cart_item_models: QueryParameter("include_cart_item_models", bool),
            include_business: QueryParameter("include_business", bool),
    ):
        user: Union[User, BusinessUser] = user
        user_settings: UserSettings = user_settings

        if user_settings.currency_type is None and user_settings.unit is None and user_settings.email is None and user_settings.phone is None:
            response.status = HttpStatus.BAD_REQUEST
            return {
                "error": "Must pass a field from 'currency_type', 'unit', 'email', 'phone'"
            }

        unit = Unit._value2member_map_[user_settings.unit] if user_settings.unit is not None else None
        user_res = user.update_fields(user_settings.email, user_settings.phone, unit, user_settings.currency_type)
        result = user_res.__getstate__()

        include_cart_item_models = include_cart_item_models if include_cart_item_models is not None and isinstance(include_cart_item_models, bool) else False
        if include_cart_item_models:
            cart_item_ids = list(map(lambda x: x.item_id, user.cart.items))
            result["cart_item_models"] = list(map(lambda item: item.__getstate__(), Item.get_items(*cart_item_ids)))

        include_business = include_business if include_business is not None and isinstance(include_business, bool) else False
        if type(user) is BusinessUser and include_business:
            result['business'] = Business.get_business_by_id(user.business_id).__getstate__()

        result['profile_picture'] = base64.b64encode(user.profile_picture.get_image('profiles/'))

        return result

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
        user.update_profile_picture(image)

        return {
            "image": base64.b64encode(pfp_data)
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
        item_id = ObjectId(item_id)
        if item_id in user.liked_items:
            return user.liked_items

        liked_items = user.liked_items.add_liked_items(item_id).liked_items
        items_collection.update_one({"_id": item_id}, {"$inc": {"mtc.lks": 1}})
        return liked_items

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

        item_id = ObjectId(item_id)
        if item_id not in user.liked_items:
            return user.liked_items

        liked_items = user.liked_items.remove_liked_item(item_id).liked_items
        items_collection.update_one({"_id": item_id}, {"$inc": {"mtc.lks": -1}})
        return liked_items

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
