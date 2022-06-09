import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from web_framework_v2 import QueryParameter, RequestBody, HttpResponse, HttpStatus

from api import auth_fail, app
from body import PaymentData
from communication import Email
from database import User, Order, orders_collection, BusinessUser, Business, Item, OrderItem, ShippingAddress
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
    @BlacklistJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order")
    def user_payment(
            token_data: BlacklistJwtTokenAuth,
            res: HttpResponse,
            payment_data: RequestBody(PaymentData)
    ):
        payment_data: PaymentData = payment_data
        user: User = token_data

        db_items = Item.get_items(*map(lambda x: x.item_id, payment_data.cart.items))
        db_subtotal = 0
        frontend_subtotal = 0

        db_cupon_discount = 0
        frontend_cupon_discount = payment_data.cart.cupon_discount

        db_shipping = 0
        frontend_shipping = payment_data.cart.shipping_cost
        business_ids = set()

        for i in range(len(payment_data.cart.items)):
            db_item = db_items[i]
            frontend_item = payment_data.cart.items[i]

            if db_item.price != frontend_item.price:
                res.status = HttpStatus.UNAUTHORIZED
                return {
                    "error": "Cannot process payment",
                    "reason": "Item costs changed while going through checkout"
                }

            db_subtotal += db_item.price * frontend_item.amount
            frontend_subtotal += frontend_item.price * frontend_item.amount

            business_ids.add(frontend_item.business_id)

        # calculate cupon discount
        db_cupon_discount = db_subtotal * (OrderController.get_cupon_discount(user, payment_data.cart.cupon, payment_data.cart.items, res) / 100)

        # calculate shipping
        db_shipping = OrderController.get_shipping_cost(user, {"items": payment_data.cart.items, "sa": payment_data.cart.shipping_address}, res)

        frontend_total = payment_data.cart.total
        db_total = db_subtotal + db_shipping - db_cupon_discount
        if db_subtotal != frontend_subtotal:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Item costs changed while going through checkout"
            }

        elif db_cupon_discount != frontend_cupon_discount:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Cupon discount changed while going through checkout"
            }

        elif db_shipping != frontend_shipping:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Shipping cost changed while going through checkout"
            }

        elif db_total != frontend_total:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "Cannot process payment",
                "reason": "Total cost changed while going through checkout"
            }

        order_items = list(map(lambda item: OrderItem(
            item_id=item.id,
            business_id=item.business_id,
            amount=item.amount,
            price=item.price,
            status=OrderStatus.Processing,
            selected_modifiers=item.selected_modifiers
        ), payment_data.cart.items))

        order = Order(
            _id=ObjectId(),
            order_date=datetime.datetime.now(),
            subtotal=db_subtotal,
            shipping_cost=db_shipping,
            cupon_discount=db_cupon_discount,
            total=db_total,
            shipping_address=payment_data.cart.shipping_address,
            items=order_items
        )

        Order.save(order)
        for business_id in business_ids:
            Business.add_order_by_id(ObjectId(business_id), order.id)

        user.order_history.add_order(order.id)

        Email().send_order_success(user.email, order)
        res.status = HttpStatus.CREATED
        return order

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order/shipping")
    def get_shipping_cost(
            user_raw: BusinessJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        return {
            'cost': 0
        }

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.get("/business/order/cupon")
    def get_cupon_discount(
            user_raw: BusinessJwtTokenAuth,
            cupon: QueryParameter("cupon"),
            res: HttpResponse
    ):
        return {
            'discount': 0
        }

    @staticmethod
    @BusinessJwtTokenAuth(on_fail=auth_fail)
    @app.post("/business/order/status")
    def update_order_status(
            user_raw: BusinessJwtTokenAuth,
            body: RequestBody(),
            res: HttpResponse
    ):
        # TODO: change status only for owning business items
        user: BusinessUser = user_raw
        order_id = body.get('order_id', None)
        item_index = body.get('item_index', None)
        status = body.get('status', None)
        if status is None or order_id is None or item_index is None:
            res.status = HttpStatus.BAD_REQUEST
            return {
                'error': 'Must pass body fields "order_id", "status" and "item_index"'
            }

        status_max = len(OrderStatus._member_map_.values())
        if not isinstance(status, int) or status >= status_max:
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"'status' body field must be an integer between 0 and {status_max}"
            }

        if not isinstance(item_index, int) or item_index < 0:
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": f"'item_index' body field must be an integer"
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

        order = Order.get_order(order_id)
        if item_index >= len(order.items):
            res.status = HttpStatus.BAD_REQUEST
            return {
                "error": "There is no item with such an index."
            }

        if order.items[item_index].business_id != business.id:
            res.status = HttpStatus.UNAUTHORIZED
            return {
                "error": "You cannot modify the status of this item."
            }

        order_doc = orders_collection.find_one_and_update({"_id": order_id}, {"$set": {f"it.{item_index}.sta": status}},
                                                          return_document=ReturnDocument.AFTER)
        return Order.document_repr_to_object(order_doc)
