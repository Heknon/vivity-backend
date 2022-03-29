from bson import ObjectId
from web_framework_v2 import PathVariable

from api import auth_fail, app
from database import User, Business, Item
from security import BlacklistJwtTokenAuth


class BusinessMetricsController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/{business_id}/view")
    def add_business_view(
            userUncast: BlacklistJwtTokenAuth,
            business_id: PathVariable("business_id"),
    ):
        user: User = userUncast
        return Business.get_business_by_id(ObjectId(business_id)).metrics.add_view()

    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/item/{item_id}/view")
    def add_item_view(
            userUncast: BlacklistJwtTokenAuth,
            item_id: PathVariable("item_id"),
    ):
        user: User = userUncast
        return Item.get_item(ObjectId(item_id)).metrics.add_view()
