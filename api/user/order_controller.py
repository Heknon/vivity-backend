from bson import ObjectId
from web_framework_v2 import QueryParameter

from api import auth_fail, app
from database import User, Order, orders_collection
from security import BlacklistJwtTokenAuth


class OrderController:
    @staticmethod
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.get("/user/order")
    def get_orders(
            user_raw: BlacklistJwtTokenAuth,
            order_ids: QueryParameter("order_ids", list)
    ):
        user: User = user_raw
        if order_ids is None:
            return {
                "error": "Must pass query parameter 'order_ids'"
            }

        user_orders = set(user.order_history.orders)
        order_ids = map(lambda x: ObjectId(x), order_ids)
        order_ids = list(filter(lambda x: x in user_orders, order_ids))
        order_docs = orders_collection.find({"_id": {"$in": order_ids}})
        return list(map(lambda doc: Order.document_repr_to_object(doc), order_docs))
