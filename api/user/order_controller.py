from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import QueryParameter, RequestBody, HttpResponse, HttpStatus

from api import auth_fail, app
from database import User, Order, orders_collection, BusinessUser, Business
from database.user import OrderStatus
from security import BlacklistJwtTokenAuth, BusinessJwtTokenAuth


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

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order/status")
    def update_order_status(
            user_raw: BusinessJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        user: BusinessUser = user_raw
        order_id = body.get('order_id', None)
        status = body.get('status', None)
        if status is None or order_id is None:
            res.status = HttpStatus.BAD_REQUEST
            return {
                'error': 'Must pass body fields "order_id" and "status"'
            }

        status_max = len(OrderStatus._member_map_.values())
        if not isinstance(status, int) or status >= status_max:
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"'status' body field must be an integer between 0 and {status_max}"
            }

        order_id = ObjectId(order_id)
        business = Business.get_business_by_id(user.business_id)

        if business is None:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Whoops, looks like you don't own a business"
            }

        if order_id not in business.orders:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "This order doesn't exist!"
            }

        order_doc = orders_collection.find_one_and_update({"_id": order_id}, {"$set": {"sta": status}}, return_document=ReturnDocument.AFTER)
        return Order.document_repr_to_object(order_doc)
